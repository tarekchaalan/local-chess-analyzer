"""Schema creation and startup recovery."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from .models import Base


async def init_db(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Anything that was running when the process died goes back to the queue.
        await conn.execute(text("UPDATE jobs SET status='queued' WHERE status='running'"))
        await conn.execute(
            text("UPDATE games SET analysis_status='queued' WHERE analysis_status='running'")
        )
