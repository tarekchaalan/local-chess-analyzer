"""Stockfish access through python-chess' async UCI client."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import chess
import chess.engine

from ..domain.types import Eval
from .settings import ENGINE_KEYS, SettingsService

log = logging.getLogger(__name__)


@dataclass(slots=True)
class EngineLine:
    move: chess.Move
    eval: Eval
    pv: list[chess.Move]


class EngineProtocol(Protocol):
    name: str
    depth: int
    time_ms: int
    threads: int
    hash_mb: int

    async def analyse(self, board: chess.Board, *, multipv: int = 2) -> list[EngineLine]: ...

    async def close(self) -> None: ...


class EngineUnavailable(Exception):
    pass


def _lines_from_info(infos: list[chess.engine.InfoDict]) -> list[EngineLine]:
    lines: list[EngineLine] = []
    for info in infos:
        pv = info.get("pv") or []
        score = info.get("score")
        if not pv or score is None:
            continue
        lines.append(EngineLine(move=pv[0], eval=Eval.from_score(score), pv=list(pv[:8])))
    return lines


class EngineSession:
    """One long-lived engine process. Restarts itself once if the process dies."""

    def __init__(self, path: str, *, threads: int, hash_mb: int, depth: int, time_ms: int):
        self.path = path
        self.threads = threads
        self.hash_mb = hash_mb
        self.depth = depth
        self.time_ms = time_ms
        self.name = "stockfish"
        self._engine: chess.engine.UciProtocol | None = None
        self._transport: asyncio.SubprocessTransport | None = None
        self._lock = asyncio.Lock()

    @property
    def limit(self) -> chess.engine.Limit:
        time_s = self.time_ms / 1000.0 if self.time_ms > 0 else None
        return chess.engine.Limit(depth=self.depth, time=time_s)

    async def start(self) -> None:
        if self._engine is not None:
            return
        if not Path(self.path).exists():
            raise EngineUnavailable(f"Engine binary not found: {self.path}")
        try:
            self._transport, self._engine = await chess.engine.popen_uci(self.path)
        except (OSError, chess.engine.EngineError) as e:
            raise EngineUnavailable(f"Could not start engine: {e}") from e
        self.name = self._engine.id.get("name", "stockfish")
        options = {"Threads": self.threads, "Hash": self.hash_mb}
        await self._engine.configure(
            {k: v for k, v in options.items() if k in self._engine.options}
        )

    async def close(self) -> None:
        engine, self._engine, self._transport = self._engine, None, None
        if engine is not None:
            try:
                await asyncio.wait_for(engine.quit(), timeout=5)
            except Exception:  # noqa: BLE001 - best effort shutdown
                pass

    async def analyse(self, board: chess.Board, *, multipv: int = 2) -> list[EngineLine]:
        async with self._lock:
            await self.start()
            assert self._engine is not None
            try:
                infos = await self._engine.analyse(board, self.limit, multipv=multipv)
            except chess.engine.EngineTerminatedError:
                log.warning("Engine died; restarting once")
                self._engine = None
                await self.start()
                assert self._engine is not None
                infos = await self._engine.analyse(board, self.limit, multipv=multipv)
        if isinstance(infos, dict):
            infos = [infos]
        return _lines_from_info(infos)

    @staticmethod
    async def validate(path: str) -> dict:
        p = Path(path)
        if not p.exists():
            return {"valid": False, "name": None, "message": "File does not exist"}
        if not p.is_file():
            return {"valid": False, "name": None, "message": "Path is not a file"}
        try:
            transport, engine = await asyncio.wait_for(chess.engine.popen_uci(str(p)), timeout=15)
        except Exception as e:  # noqa: BLE001
            return {"valid": False, "name": None, "message": f"Not a UCI engine: {e}"}
        name = engine.id.get("name", "unknown")
        try:
            await asyncio.wait_for(engine.quit(), timeout=5)
        except Exception:  # noqa: BLE001
            transport.close()
        return {"valid": True, "name": name, "message": f"{name} is ready"}


class EngineProvider:
    """Builds the shared EngineSession from settings and rebuilds it when they change."""

    def __init__(self, settings: SettingsService):
        self._settings = settings
        self._session: EngineSession | None = None
        self._lock = asyncio.Lock()

    async def get(self) -> EngineSession:
        async with self._lock:
            if self._session is None:
                s = await self._settings.get_all()
                self._session = EngineSession(
                    await self._settings.engine_path(),
                    threads=int(s["engine_threads"]),
                    hash_mb=int(s["engine_hash_mb"]),
                    depth=int(s["analysis_depth"]),
                    time_ms=int(s["analysis_time_ms"]),
                )
            return self._session

    async def invalidate(self, changed_keys: set[str] | None = None) -> None:
        """Drop the session. Search-limit changes only need a settings refresh."""
        async with self._lock:
            session, self._session = self._session, None
        if session is not None:
            if changed_keys is None or changed_keys & ENGINE_KEYS:
                await session.close()
            else:
                # keep the process, just forget the wrapper so limits are re-read
                s = await self._settings.get_all()
                session.depth = int(s["analysis_depth"])
                session.time_ms = int(s["analysis_time_ms"])
                async with self._lock:
                    self._session = session

    async def close(self) -> None:
        async with self._lock:
            session, self._session = self._session, None
        if session is not None:
            await session.close()
