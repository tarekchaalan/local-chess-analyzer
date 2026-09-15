from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI

from lca.config import Paths
from lca.main import create_app


@pytest.fixture
def paths(tmp_path: Path) -> Paths:
    return Paths(base=tmp_path)


@pytest.fixture
def app(paths: Paths) -> FastAPI:
    return create_app(paths)


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
            yield c
