from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI

from lca.config import Paths
from lca.main import create_app

from .fakes import FakeEngineProvider, fake_platform_factory


@pytest.fixture
def paths(tmp_path: Path) -> Paths:
    return Paths(base=tmp_path)


@pytest.fixture
def app(paths: Paths) -> FastAPI:
    return create_app(
        paths,
        platform_factory=fake_platform_factory,
        engine_provider_factory=FakeEngineProvider,
    )


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
            yield c


async def wait_until(pred, timeout: float = 5.0) -> bool:
    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout
    while loop.time() < deadline:
        if await pred():
            return True
        await asyncio.sleep(0.02)
    return False


async def wait_for_job(client: httpx.AsyncClient, job_id: int, timeout: float = 5.0) -> dict:
    async def done():
        r = await client.get(f"/api/jobs/{job_id}")
        return r.status_code == 200 and r.json()["status"] in ("done", "failed", "cancelled")

    assert await wait_until(done, timeout), "job did not finish"
    return (await client.get(f"/api/jobs/{job_id}")).json()
