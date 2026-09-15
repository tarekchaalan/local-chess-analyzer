"""Async SQLite engine and session factory."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

SessionFactory = async_sessionmaker[AsyncSession]


def make_engine(db_path: Path | str) -> AsyncEngine:
    url = f"sqlite+aiosqlite:///{db_path}"
    engine = create_async_engine(url, echo=False)

    @event.listens_for(engine.sync_engine, "connect")
    def _pragmas(dbapi_conn, _record):  # pragma: no cover - trivial
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.execute("PRAGMA journal_mode=WAL")
        cur.execute("PRAGMA synchronous=NORMAL")
        cur.close()

    return engine


def make_session_factory(engine: AsyncEngine) -> SessionFactory:
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
