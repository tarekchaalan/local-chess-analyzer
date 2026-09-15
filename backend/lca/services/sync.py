"""Pull games for one linked account into the games table."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert

from ..db.engine import SessionFactory
from ..db.models import Account, Game, utcnow_iso
from ..domain.pgn import parse_game, result_for
from ..platforms.base import NormalizedGame, Platform, PlatformError

log = logging.getLogger(__name__)

ProgressCb = Callable[[int, int, str | None], Awaitable[None]]
CancelCheck = Callable[[], bool]
EnqueueAnalyze = Callable[[int], Awaitable[None]]

BATCH = 100
MAX_RATE_LIMIT_RETRIES = 3


class SyncCancelled(Exception):
    pass


def _game_row(account: Account, g: NormalizedGame) -> dict | None:
    w, b = g.white.lower(), g.black.lower()
    if account.username_key == w:
        color = "w"
    elif account.username_key == b:
        color = "b"
    else:
        return None
    try:
        ply_count = sum(1 for _ in parse_game(g.pgn).mainline_moves())
    except ValueError:
        return None
    return {
        "account_id": account.id,
        "platform": g.platform,
        "platform_game_id": g.platform_game_id,
        "url": g.url,
        "pgn": g.pgn,
        "white": g.white,
        "black": g.black,
        "white_rating": g.white_rating,
        "black_rating": g.black_rating,
        "user_color": color,
        "result": g.result,
        "user_result": result_for(color, g.result),
        "termination": g.termination,
        "time_class": g.time_class,
        "time_control": g.time_control,
        "rated": g.rated,
        "played_at": g.played_at.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "eco": g.eco,
        "opening_name": g.opening_name,
        "platform_accuracy_white": g.platform_accuracy_white,
        "platform_accuracy_black": g.platform_accuracy_black,
        "ply_count": ply_count,
        "imported_at": utcnow_iso(),
        "analysis_status": "none",
    }


async def _insert_batch(sf: SessionFactory, rows: list[dict]) -> list[int]:
    """Insert rows, ignoring duplicates. Returns ids of newly created games."""
    created: list[int] = []
    async with sf() as session:
        for row in rows:
            stmt = (
                insert(Game)
                .values(**row)
                .on_conflict_do_nothing(index_elements=["platform", "platform_game_id"])
            )
            result = await session.execute(stmt)
            if result.rowcount:
                created.append(int(result.inserted_primary_key[0]))
        await session.commit()
    return created


async def _save_cursor(sf: SessionFactory, account_id: int, cursor: str | None) -> None:
    async with sf() as session:
        account = await session.get(Account, account_id)
        if account is not None:
            account.sync_cursor = cursor
            await session.commit()


async def refresh_counts(sf: SessionFactory, account_id: int, *, completed: bool) -> Account:
    """Recompute game_count; stamp last_synced_at only when the sync ran to completion."""
    async with sf() as session:
        account = await session.get(Account, account_id)
        assert account is not None
        count = await session.scalar(
            select(func.count()).select_from(Game).where(Game.account_id == account_id)
        )
        account.game_count = int(count or 0)
        if completed:
            account.last_synced_at = utcnow_iso()
        await session.commit()
        await session.refresh(account)
        return account


async def sync_account(
    sf: SessionFactory,
    account_id: int,
    platform: Platform,
    *,
    months: int | None = None,
    on_progress: ProgressCb | None = None,
    is_cancelled: CancelCheck | None = None,
    enqueue_analyze: EnqueueAnalyze | None = None,
) -> dict[str, int]:
    async with sf() as session:
        account = await session.get(Account, account_id)
    if account is None:
        raise ValueError("account_not_found")

    cursor = account.sync_cursor if not months else None
    total = 0
    count_archives = getattr(platform, "count_archives", None)
    if count_archives is not None:
        total = await count_archives(account.username, cursor, months)

    fetched = 0
    created_total = 0
    archives_done = 0
    last_cursor = cursor
    pending: list[dict] = []
    retries = 0

    async def flush() -> None:
        nonlocal created_total, pending
        if not pending:
            return
        created = await _insert_batch(sf, pending)
        created_total += len(created)
        pending = []
        if enqueue_analyze:
            for gid in created:
                await enqueue_analyze(gid)

    async def report(message: str) -> None:
        if on_progress:
            await on_progress(archives_done if total else fetched, total, message)

    completed = False
    try:
        while True:
            try:
                async for game, new_cursor in platform.fetch_games(
                    account.username, last_cursor, months=months
                ):
                    if is_cancelled and is_cancelled():
                        raise SyncCancelled()
                    fetched += 1
                    row = _game_row(account, game)
                    if row is not None:
                        pending.append(row)
                    cursor_changed = new_cursor != last_cursor
                    if cursor_changed and total:
                        archives_done += 1
                    if len(pending) >= BATCH or cursor_changed:
                        await flush()
                        last_cursor = new_cursor
                        await _save_cursor(sf, account_id, last_cursor)
                        await report(f"{fetched} games fetched, {created_total} new")
                break
            except PlatformError as e:
                if e.code == "rate_limited" and retries < MAX_RATE_LIMIT_RETRIES:
                    retries += 1
                    wait = e.retry_after or 30.0
                    log.info("Rate limited by %s; waiting %.0fs", platform.name, wait)
                    await report(f"Rate limited, waiting {wait:.0f}s")
                    await asyncio.sleep(wait)
                    continue
                raise
        await flush()
        await _save_cursor(sf, account_id, last_cursor)
        completed = True
    finally:
        # Keep whatever was imported, even on cancel or failure.
        await flush()
        await refresh_counts(sf, account_id, completed=completed)

    await report(f"{created_total} new games")
    return {"fetched": fetched, "created": created_total}
