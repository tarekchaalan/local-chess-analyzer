"""Application factory."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api import health
from .api.errors import install_error_handlers
from .config import Paths
from .db.bootstrap import init_db
from .db.engine import make_engine, make_session_factory
from .services.settings import SettingsService

log = logging.getLogger("lca")

DEV_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]


def create_app(paths: Paths | None = None) -> FastAPI:
    paths = paths or Paths()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = make_engine(paths.db_path())
        app.state.paths = paths
        app.state.db_engine = engine
        app.state.session_factory = make_session_factory(engine)
        app.state.settings = SettingsService(app.state.session_factory, paths)
        await init_db(engine)
        try:
            yield
        finally:
            await engine.dispose()

    app = FastAPI(title="Local Chess Analyzer", version="2.0.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=DEV_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_error_handlers(app)

    app.include_router(health.router, prefix="/api")

    dist = paths.frontend_dist_dir()
    if dist is not None:
        app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")

    return app


app = create_app()
