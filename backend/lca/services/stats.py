"""Aggregate queries over games and analyses."""

from __future__ import annotations

from sqlalchemy import Select, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..api.schemas import (
    OpeningStat,
    OverviewOut,
    ResultCounts,
    ResultsByColorOut,
    TimeClassStat,
    TrendPoint,
)
from ..db.models import Account, Analysis, Game


def _user_accuracy():
    return case((Game.user_color == "w", Analysis.accuracy_white), else_=Analysis.accuracy_black)


def _user_count(label: str):
    return case(
        (Game.user_color == "w", func.json_extract(Analysis.counts, f"$.w.{label}")),
        else_=func.json_extract(Analysis.counts, f"$.b.{label}"),
    )


def _wins():
    return func.sum(case((Game.user_result == "win", 1), else_=0))


def _draws():
    return func.sum(case((Game.user_result == "draw", 1), else_=0))


def _losses():
    return func.sum(case((Game.user_result == "loss", 1), else_=0))


def _rate(wins: int, games: int) -> float | None:
    return round(100.0 * wins / games, 1) if games else None


def _scope(stmt: Select, account_id: int | None) -> Select:
    return stmt.where(Game.account_id == account_id) if account_id is not None else stmt


def _counts(games: int, wins: int, draws: int, losses: int) -> ResultCounts:
    return ResultCounts(
        games=games, wins=wins, draws=draws, losses=losses, win_rate=_rate(wins, games)
    )


async def overview(session: AsyncSession, account_id: int | None) -> OverviewOut:
    stmt = _scope(
        select(
            func.count(Game.id),
            _wins(),
            _draws(),
            _losses(),
            func.count(Analysis.game_id),
            func.avg(_user_accuracy()),
        ).outerjoin(Analysis, Analysis.game_id == Game.id),
        account_id,
    )
    games, wins, draws, losses, analyzed, acc = (await session.execute(stmt)).one()
    accounts = int(await session.scalar(select(func.count(Account.id))) or 0)
    return OverviewOut(
        games=int(games or 0),
        wins=int(wins or 0),
        draws=int(draws or 0),
        losses=int(losses or 0),
        win_rate=_rate(int(wins or 0), int(games or 0)),
        analyzed=int(analyzed or 0),
        mean_accuracy=round(float(acc), 1) if acc is not None else None,
        accounts=accounts,
    )


async def accuracy_trend(
    session: AsyncSession, account_id: int | None, bucket: str
) -> list[TrendPoint]:
    fmt = "%Y-W%W" if bucket == "week" else "%Y-%m"
    bucket_expr = func.strftime(fmt, Game.played_at)
    stmt = _scope(
        select(bucket_expr, func.count(Game.id), func.avg(_user_accuracy()))
        .join(Analysis, Analysis.game_id == Game.id)
        .group_by(bucket_expr)
        .order_by(bucket_expr),
        account_id,
    )
    rows = (await session.execute(stmt)).all()
    return [
        TrendPoint(bucket=b, games=int(n), accuracy=round(float(a), 1))
        for b, n, a in rows
        if a is not None
    ]


async def by_time_class(session: AsyncSession, account_id: int | None) -> list[TimeClassStat]:
    stmt = _scope(
        select(
            Game.time_class,
            func.count(Game.id),
            _wins(),
            _draws(),
            _losses(),
            func.count(Analysis.game_id),
            func.avg(_user_accuracy()),
            func.avg(_user_count("blunder")),
            func.avg(_user_count("mistake")),
        )
        .outerjoin(Analysis, Analysis.game_id == Game.id)
        .group_by(Game.time_class)
        .order_by(func.count(Game.id).desc()),
        account_id,
    )
    out = []
    for tc, games, wins, draws, losses, analyzed, acc, bl, mi in await session.execute(stmt):
        out.append(
            TimeClassStat(
                time_class=tc,
                games=int(games),
                wins=int(wins or 0),
                draws=int(draws or 0),
                losses=int(losses or 0),
                win_rate=_rate(int(wins or 0), int(games)),
                analyzed=int(analyzed or 0),
                mean_accuracy=round(float(acc), 1) if acc is not None else None,
                blunders_per_game=round(float(bl), 2) if bl is not None else None,
                mistakes_per_game=round(float(mi), 2) if mi is not None else None,
            )
        )
    return out


async def openings(
    session: AsyncSession, account_id: int | None, color: str | None, limit: int
) -> list[OpeningStat]:
    name = func.coalesce(Analysis.opening_name, Game.opening_name)
    eco = func.coalesce(Analysis.opening_eco, Game.eco)
    stmt = (
        select(eco, name, func.count(Game.id), _wins(), _draws(), _losses())
        .outerjoin(Analysis, Analysis.game_id == Game.id)
        .where(name.is_not(None))
        .group_by(name)
        .order_by(func.count(Game.id).desc(), name)
        .limit(limit)
    )
    stmt = _scope(stmt, account_id)
    if color in ("w", "b"):
        stmt = stmt.where(Game.user_color == color)
    rows = (await session.execute(stmt)).all()
    return [
        OpeningStat(
            eco=e,
            name=n,
            games=int(g),
            wins=int(w or 0),
            draws=int(d or 0),
            losses=int(losses or 0),
            win_rate=_rate(int(w or 0), int(g)),
        )
        for e, n, g, w, d, losses in rows
    ]


async def results_by_color(session: AsyncSession, account_id: int | None) -> ResultsByColorOut:
    stmt = _scope(
        select(Game.user_color, func.count(Game.id), _wins(), _draws(), _losses()).group_by(
            Game.user_color
        ),
        account_id,
    )
    per = {c: _counts(int(g), int(w or 0), int(d or 0), int(losses or 0))
           for c, g, w, d, losses in (await session.execute(stmt))}  # fmt: skip
    empty = _counts(0, 0, 0, 0)
    return ResultsByColorOut(white=per.get("w", empty), black=per.get("b", empty))
