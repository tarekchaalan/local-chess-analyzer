"""FastAPI dependencies that pull shared objects off app.state."""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.settings import SettingsService


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.session_factory() as session:
        yield session


def get_settings(request: Request) -> SettingsService:
    return request.app.state.settings
