from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlalchemy.sql import text
import os

from backend.app.db.database import engine, Base
from backend.app.db.models import Game, Setting
from backend.app.paths import data_dir, frontend_dist_dir, stockfish_binary_path
from backend.app.api import settings as settings_api
from backend.app.api import sync as sync_api
from backend.app.api import games as games_api
from backend.app.api import system_resources as system_resources_api
from backend.app.api import database as database_api

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure data directory exists
    _data_dir = data_dir()
    _data_dir.mkdir(parents=True, exist_ok=True)
    db_path = _data_dir / "games.db"

    # Ensure Stockfish binary is executable (for macOS/Linux when bundled)
    try:
        sf_path = stockfish_binary_path()
        if sf_path.exists():
            os.chmod(sf_path, 0o755)
    except Exception:
        # Non-fatal; validation endpoint will indicate if it's not executable
        pass

    # Initialize database tables and default settings
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("INSERT OR IGNORE INTO settings (key, value) VALUES ('chess_com_username', NULL)"))
        await conn.execute(
            text("INSERT OR IGNORE INTO settings (key, value) VALUES ('stockfish_path', :sf)"),
            {"sf": str(stockfish_binary_path())}
        )
        await conn.execute(text("INSERT OR IGNORE INTO settings (key, value) VALUES ('stockfish_threads', '1')"))
        await conn.execute(text("INSERT OR IGNORE INTO settings (key, value) VALUES ('stockfish_hash_mb', '128')"))
        await conn.execute(text("INSERT OR IGNORE INTO settings (key, value) VALUES ('analysis_depth', '15')"))
        await conn.execute(text("INSERT OR IGNORE INTO settings (key, value) VALUES ('analysis_time_ms', '1000')"))
        await conn.execute(text("INSERT OR IGNORE INTO settings (key, value) VALUES ('auto_sync_enabled', 'false')"))
        await conn.execute(text("INSERT OR IGNORE INTO settings (key, value) VALUES ('theme', 'default')"))

    yield


app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(settings_api.router)
app.include_router(sync_api.router)
app.include_router(games_api.router)
app.include_router(system_resources_api.router)
app.include_router(database_api.router)

# Serve built frontend if available
_frontend_dir = frontend_dist_dir()
if _frontend_dir.exists():
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")

