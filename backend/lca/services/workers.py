"""Job handlers: glue between the JobRunner and the sync / analysis services."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy import delete, update

from ..db.engine import SessionFactory
from ..db.models import Account, Analysis, Game, Job
from ..domain.openings import OpeningBook
from ..platforms.base import Platform
from .analysis import AnalysisCancelled, analyze_game
from .engine import EngineProvider, EngineUnavailable
from .jobs import EventBus, JobCancelled, JobContext, JobRunner
from .settings import SettingsService
from .sync import SyncCancelled, sync_account

log = logging.getLogger(__name__)

PlatformFactory = Callable[[str, dict[str, str]], Platform]


@dataclass
class Workers:
    sf: SessionFactory
    bus: EventBus
    settings: SettingsService
    engines: EngineProvider
    book: OpeningBook
    platform_factory: PlatformFactory
    runner: JobRunner | None = None

    # ---- helpers ------------------------------------------------------------------

    async def _set_game_status(self, game_id: int, status: str) -> None:
        async with self.sf() as session:
            await session.execute(
                update(Game).where(Game.id == game_id).values(analysis_status=status)
            )
            await session.commit()
        self.bus.publish("game", {"id": game_id, "analysis_status": status})

    async def enqueue_analyze(self, game_id: int) -> Job:
        assert self.runner is not None
        job = await self.runner.enqueue("analyze", game_id=game_id)
        await self._set_game_status(game_id, "queued")
        return job

    async def enqueue_sync(self, account_id: int, months: int | None = None) -> Job:
        assert self.runner is not None
        params = {"months": months} if months else None
        return await self.runner.enqueue("sync", account_id=account_id, params=params)

    # ---- handlers -----------------------------------------------------------------

    async def analyze_handler(self, job: Job, ctx: JobContext) -> None:
        assert job.game_id is not None
        game_id = job.game_id
        async with self.sf() as session:
            game = await session.get(Game, game_id)
        if game is None:
            raise RuntimeError("game_not_found")
        await self._set_game_status(game_id, "running")
        try:
            engine = await self.engines.get()
            report = await analyze_game(
                game.pgn,
                engine,
                self.book,
                on_progress=lambda done, total: ctx.progress(done, total),
                is_cancelled=ctx.is_cancelled,
            )
        except (AnalysisCancelled, JobCancelled):
            await self._set_game_status(game_id, "none")
            raise JobCancelled() from None
        except EngineUnavailable as e:
            await self._set_game_status(game_id, "failed")
            raise RuntimeError(f"engine_unavailable: {e}") from e
        except ValueError as e:
            await self._set_game_status(game_id, "failed")
            raise RuntimeError(str(e)) from e
        except Exception:
            await self._set_game_status(game_id, "failed")
            raise

        async with self.sf() as session:
            await session.execute(delete(Analysis).where(Analysis.game_id == game_id))
            session.add(
                Analysis(
                    game_id=game_id,
                    engine_name=report.engine_name,
                    depth=report.depth,
                    time_ms=report.time_ms,
                    multipv=report.multipv,
                    threads=report.threads,
                    hash_mb=report.hash_mb,
                    accuracy_white=report.accuracy_white,
                    accuracy_black=report.accuracy_black,
                    opening_eco=report.opening_eco,
                    opening_name=report.opening_name,
                    book_plies=report.book_plies,
                    counts=report.counts,
                    moves=report.moves,
                )
            )
            await session.commit()
        await self._set_game_status(game_id, "done")

    async def sync_handler(self, job: Job, ctx: JobContext) -> None:
        assert job.account_id is not None
        async with self.sf() as session:
            account = await session.get(Account, job.account_id)
        if account is None:
            raise RuntimeError("account_not_found")
        settings = await self.settings.get_all()
        platform = self.platform_factory(account.platform, settings)
        months = (job.params or {}).get("months")
        auto = settings.get("auto_analyze_new_games") == "true"

        async def enqueue(game_id: int) -> None:
            await self.enqueue_analyze(game_id)

        try:
            await sync_account(
                self.sf,
                account.id,
                platform,
                months=months,
                on_progress=ctx.progress,
                is_cancelled=ctx.is_cancelled,
                enqueue_analyze=enqueue if auto else None,
            )
        except SyncCancelled:
            raise JobCancelled() from None
        finally:
            aclose = getattr(platform, "aclose", None)
            if aclose is not None:
                await aclose()
            async with self.sf() as session:
                fresh = await session.get(Account, account.id)
            if fresh is not None:
                self.bus.publish(
                    "account",
                    {
                        "id": fresh.id,
                        "game_count": fresh.game_count,
                        "last_synced_at": fresh.last_synced_at,
                    },
                )

    def handlers(self) -> dict:
        return {"analyze": self.analyze_handler, "sync": self.sync_handler}
