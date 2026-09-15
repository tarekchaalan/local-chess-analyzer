from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..services import stats
from .deps import get_session
from .schemas import OpeningStat, OverviewOut, ResultsByColorOut, TimeClassStat, TrendPoint

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=OverviewOut)
async def overview(
    account_id: int | None = None, session: AsyncSession = Depends(get_session)
) -> OverviewOut:
    return await stats.overview(session, account_id)


@router.get("/accuracy-trend", response_model=list[TrendPoint])
async def accuracy_trend(
    bucket: Literal["week", "month"] = "month",
    account_id: int | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[TrendPoint]:
    return await stats.accuracy_trend(session, account_id, bucket)


@router.get("/by-time-class", response_model=list[TimeClassStat])
async def by_time_class(
    account_id: int | None = None, session: AsyncSession = Depends(get_session)
) -> list[TimeClassStat]:
    return await stats.by_time_class(session, account_id)


@router.get("/openings", response_model=list[OpeningStat])
async def openings(
    account_id: int | None = None,
    color: Literal["w", "b"] | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> list[OpeningStat]:
    return await stats.openings(session, account_id, color, limit)


@router.get("/results", response_model=ResultsByColorOut)
async def results(
    account_id: int | None = None, session: AsyncSession = Depends(get_session)
) -> ResultsByColorOut:
    return await stats.results_by_color(session, account_id)
