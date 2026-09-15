from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import Analysis, Game
from ..services.games import SORT_FIELDS, GameFilters, list_games, to_game_out
from ..services.jobs import job_to_dict
from .deps import get_session
from .errors import ApiError
from .schemas import (
    AnalysisOut,
    AnalyzeRequest,
    BulkAnalyzeRequest,
    BulkAnalyzeResponse,
    GameListResponse,
    GameOut,
    JobOut,
)

router = APIRouter(prefix="/games", tags=["games"])


async def _get_or_404(session: AsyncSession, game_id: int) -> Game:
    game = await session.get(Game, game_id)
    if game is None:
        raise ApiError(404, "not_found", "Game not found")
    return game


@router.get("", response_model=GameListResponse)
async def get_games(
    session: AsyncSession = Depends(get_session),
    account_id: int | None = None,
    platform: Literal["chesscom", "lichess"] | None = None,
    time_class: str | None = None,
    user_result: Literal["win", "loss", "draw"] | None = None,
    color: Literal["w", "b"] | None = None,
    analysis_status: str | None = None,
    search: str | None = None,
    date_from: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    date_to: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    sort: str = "played_at",
    order: Literal["asc", "desc"] = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=200),
) -> GameListResponse:
    if sort not in SORT_FIELDS:
        raise ApiError(400, "validation_error", f"sort must be one of {', '.join(SORT_FIELDS)}")
    filters = GameFilters(
        account_id=account_id,
        platform=platform,
        time_class=time_class,
        user_result=user_result,
        color=color,
        analysis_status=analysis_status,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )
    items, total = await list_games(
        session, filters, sort=sort, order=order, page=page, page_size=page_size
    )
    return GameListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{game_id}", response_model=GameOut)
async def get_game(game_id: int, session: AsyncSession = Depends(get_session)) -> GameOut:
    game = await _get_or_404(session, game_id)
    analysis = await session.get(Analysis, game_id)
    accuracy = None
    if analysis is not None:
        accuracy = analysis.accuracy_white if game.user_color == "w" else analysis.accuracy_black
    return to_game_out(game, accuracy)


@router.get("/{game_id}/analysis", response_model=AnalysisOut)
async def get_analysis(game_id: int, session: AsyncSession = Depends(get_session)) -> AnalysisOut:
    await _get_or_404(session, game_id)
    analysis = await session.get(Analysis, game_id)
    if analysis is None:
        raise ApiError(404, "no_analysis", "This game has not been analysed yet")
    return AnalysisOut(
        game_id=analysis.game_id,
        engine_name=analysis.engine_name,
        depth=analysis.depth,
        time_ms=analysis.time_ms,
        multipv=analysis.multipv,
        threads=analysis.threads,
        hash_mb=analysis.hash_mb,
        created_at=analysis.created_at,
        accuracy_white=analysis.accuracy_white,
        accuracy_black=analysis.accuracy_black,
        opening_eco=analysis.opening_eco,
        opening_name=analysis.opening_name,
        book_plies=analysis.book_plies,
        counts=analysis.counts,
        moves=analysis.moves,
    )


@router.post("/{game_id}/analyze", response_model=JobOut, status_code=202)
async def analyze(
    game_id: int,
    request: Request,
    body: AnalyzeRequest | None = None,
    session: AsyncSession = Depends(get_session),
) -> JobOut:
    game = await _get_or_404(session, game_id)
    force = body.force if body else False
    if game.analysis_status == "done" and not force:
        raise ApiError(409, "already_analyzed", "Game is already analysed; pass force to redo")
    job = await request.app.state.workers.enqueue_analyze(game_id)
    return JobOut(**job_to_dict(job))


@router.post("/analyze", response_model=BulkAnalyzeResponse, status_code=202)
async def bulk_analyze(
    body: BulkAnalyzeRequest, request: Request, session: AsyncSession = Depends(get_session)
) -> BulkAnalyzeResponse:
    ids = list(dict.fromkeys(body.game_ids))
    rows = (await session.execute(select(Game).where(Game.id.in_(ids)))).scalars().all()
    by_id = {g.id: g for g in rows}
    jobs, skipped = [], []
    for gid in ids:
        game = by_id.get(gid)
        if game is None or (game.analysis_status == "done" and not body.force):
            skipped.append(gid)
            continue
        job = await request.app.state.workers.enqueue_analyze(gid)
        jobs.append(JobOut(**job_to_dict(job)))
    return BulkAnalyzeResponse(jobs=jobs, skipped=skipped)


@router.delete("/{game_id}/analysis", status_code=204)
async def delete_analysis(
    game_id: int, request: Request, session: AsyncSession = Depends(get_session)
) -> None:
    await _get_or_404(session, game_id)
    analysis = await session.get(Analysis, game_id)
    if analysis is not None:
        await session.delete(analysis)
    await session.execute(update(Game).where(Game.id == game_id).values(analysis_status="none"))
    await session.commit()
    request.app.state.bus.publish("game", {"id": game_id, "analysis_status": "none"})
