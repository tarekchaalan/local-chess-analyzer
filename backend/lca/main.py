"""Application factory."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api import accounts, health, jobs
from .api.errors import install_error_handlers
from .config import Paths
from .db.bootstrap import init_db
from .db.engine import make_engine, make_session_factory
from .domain.openings import OpeningBook
from .platforms.base import Platform, get_platform
from .services.engine import EngineProvider
from .services.jobs import EventBus, JobRunner
from .services.settings import SettingsService
from .services.workers import PlatformFactory, Workers

log = logging.getLogger("lca")

DEV_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


def default_platform_factory(name: str, settings: dict[str, str]) -> Platform:
    return get_platform(name, lichess_token=settings.get("lichess_token") or None)


def create_app(
    paths: Paths | None = None,
    *,
    platform_factory: PlatformFactory | None = None,
    engine_provider_factory=None,
    book: OpeningBook | None = None,
) -> FastAPI:
    paths = paths or Paths()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = make_engine(paths.db_path())
        sf = make_session_factory(engine)
        settings = SettingsService(sf, paths)
        bus = EventBus()
        engines = (
            engine_provider_factory(settings)
            if engine_provider_factory
            else EngineProvider(settings)
        )
        workers = Workers(
            sf=sf,
            bus=bus,
            settings=settings,
            engines=engines,
            book=book or OpeningBook.load(paths.openings_path()),
            platform_factory=platform_factory or default_platform_factory,
        )
        runner = JobRunner(sf, bus, workers.handlers())
        workers.runner = runner

        app.state.paths = paths
        app.state.db_engine = engine
        app.state.session_factory = sf
        app.state.settings = settings
        app.state.bus = bus
        app.state.engines = engines
        app.state.workers = workers
        app.state.runner = runner

        await init_db(engine)
        await runner.start()
        try:
            yield
        finally:
            await runner.stop()
            await engines.close()
            await engine.dispose()

    app = FastAPI(title="Local Chess Analyzer", version="2.0.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=DEV_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_error_handlers(app)

    for router in (health.router, accounts.router, jobs.router):
        app.include_router(router, prefix="/api")

    dist = paths.frontend_dist_dir()
    if dist is not None:
        app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")

    return app


app = create_app()
