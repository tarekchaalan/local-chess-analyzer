"""Export / import / reset of the SQLite file."""

from __future__ import annotations

import asyncio
import shutil
import sqlite3
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.bootstrap import init_db
from ..db.models import Account, Analysis, Game, Job
from .deps import get_session
from .errors import ApiError
from .schemas import DatabaseImportOut, DatabaseResetOut

router = APIRouter(prefix="/database", tags=["database"])

REQUIRED_TABLES = {"accounts", "games", "analyses", "settings"}


def _remove(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _sidecars(db_path: Path) -> list[Path]:
    return [db_path.with_name(db_path.name + "-wal"), db_path.with_name(db_path.name + "-shm")]


@router.get("/export")
async def export_database(request: Request, background: BackgroundTasks) -> FileResponse:
    engine = request.app.state.db_engine
    db_path: Path = request.app.state.paths.db_path()
    if not db_path.exists():
        raise ApiError(404, "not_found", "Database file not found")
    async with engine.begin() as conn:
        await conn.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
    tmp = Path(tempfile.mkdtemp(prefix="lca-export-")) / "lca.db"
    # sqlite backup API gives a consistent snapshot even with open connections
    src = sqlite3.connect(db_path)
    dst = sqlite3.connect(tmp)
    with dst:
        src.backup(dst)
    src.close()
    dst.close()
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    background.add_task(shutil.rmtree, tmp.parent, True)
    return FileResponse(
        tmp,
        media_type="application/vnd.sqlite3",
        filename=f"lca-backup-{stamp}.db",
        headers={"Cache-Control": "no-store"},
    )


def _inspect_sqlite(path: Path) -> tuple[int, int]:
    try:
        # Not read-only: a WAL-mode file needs to create its -shm sidecar to be opened.
        conn = sqlite3.connect(path)
        try:
            tables = {
                r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
            missing = REQUIRED_TABLES - tables
            if missing:
                raise ApiError(
                    400, "invalid_database", f"Missing tables: {', '.join(sorted(missing))}"
                )
            games = conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]
            accounts = conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
        finally:
            conn.close()
    except sqlite3.DatabaseError as e:
        raise ApiError(400, "invalid_database", f"Not a valid SQLite database: {e}") from e
    return int(games), int(accounts)


@router.post("/import", response_model=DatabaseImportOut)
async def import_database(request: Request, file: UploadFile = File(...)) -> DatabaseImportOut:
    state = request.app.state
    db_path: Path = state.paths.db_path()
    tmp = db_path.with_name("lca.import.tmp")
    with tmp.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            out.write(chunk)
    try:
        games, accounts = _inspect_sqlite(tmp)
    except ApiError:
        _remove(tmp)
        raise

    await state.runner.cancel_all()
    await asyncio.sleep(0.2)
    await state.engines.close()
    await state.db_engine.dispose()

    backup: Path | None = None
    if db_path.exists():
        backup = db_path.with_name(f"lca.backup-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}.db")
        shutil.copy2(db_path, backup)
    for side in _sidecars(db_path):
        _remove(side)
    shutil.move(tmp, db_path)
    await init_db(state.db_engine)
    state.settings._cache = None
    return DatabaseImportOut(
        games=games, accounts=accounts, backup_path=str(backup) if backup else None
    )


@router.post("/reset", response_model=DatabaseResetOut)
async def reset_database(
    request: Request, session: AsyncSession = Depends(get_session)
) -> DatabaseResetOut:
    await request.app.state.runner.cancel_all()
    games = int(await session.scalar(select(func.count(Game.id))) or 0)
    accounts = int(await session.scalar(select(func.count(Account.id))) or 0)
    for model in (Job, Analysis, Game, Account):
        await session.execute(delete(model))
    await session.commit()
    async with request.app.state.db_engine.begin() as conn:
        await conn.execute(text("VACUUM"))
    return DatabaseResetOut(deleted_games=games, deleted_accounts=accounts)
