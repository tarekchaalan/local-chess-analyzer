"""Game list query building and row -> schema mapping."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Select, and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..api.schemas import GameListItem, GameOut
from ..db.models import Analysis, Game

SORT_FIELDS = ("played_at", "accuracy", "rating")


@dataclass(slots=True)
class GameFilters:
    account_id: int | None = None
    platform: str | None = None
    time_class: str | None = None
    user_result: str | None = None
    color: str | None = None
    analysis_status: str | None = None
    search: str | None = None
    date_from: str | None = None
    date_to: str | None = None


def _user_accuracy_expr():
    return case(
        (Game.user_color == "w", Analysis.accuracy_white),
        else_=Analysis.accuracy_black,
    )


def _opponent_rating_expr():
    return case((Game.user_color == "w", Game.black_rating), else_=Game.white_rating)


def apply_filters(stmt: Select, f: GameFilters) -> Select:
    conds = []
    if f.account_id is not None:
        conds.append(Game.account_id == f.account_id)
    if f.platform:
        conds.append(Game.platform == f.platform)
    if f.time_class:
        conds.append(Game.time_class == f.time_class)
    if f.user_result:
        conds.append(Game.user_result == f.user_result)
    if f.color in ("w", "b"):
        conds.append(Game.user_color == f.color)
    if f.analysis_status:
        conds.append(Game.analysis_status == f.analysis_status)
    if f.search:
        needle = f"%{f.search.strip().lower()}%"
        opponent = case((Game.user_color == "w", Game.black), else_=Game.white)
        conds.append(
            or_(
                func.lower(opponent).like(needle),
                func.lower(func.coalesce(Game.opening_name, "")).like(needle),
            )
        )
    if f.date_from:
        conds.append(Game.played_at >= f.date_from)
    if f.date_to:
        conds.append(Game.played_at <= f.date_to + "T23:59:59Z")
    return stmt.where(and_(*conds)) if conds else stmt


def base_query() -> Select:
    return select(Game, _user_accuracy_expr().label("accuracy")).outerjoin(
        Analysis, Analysis.game_id == Game.id
    )


def order_query(stmt: Select, sort: str, order: str) -> Select:
    desc = order != "asc"
    if sort == "accuracy":
        col = _user_accuracy_expr()
        # nulls last regardless of direction
        stmt = stmt.order_by(col.is_(None), col.desc() if desc else col.asc())
    elif sort == "rating":
        col = _opponent_rating_expr()
        stmt = stmt.order_by(col.is_(None), col.desc() if desc else col.asc())
    else:
        stmt = stmt.order_by(Game.played_at.desc() if desc else Game.played_at.asc())
    return stmt.order_by(Game.id.desc() if desc else Game.id.asc())


async def list_games(
    session: AsyncSession, f: GameFilters, *, sort: str, order: str, page: int, page_size: int
) -> tuple[list[GameListItem], int]:
    stmt = order_query(apply_filters(base_query(), f), sort, order)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    rows = (await session.execute(stmt)).all()
    count_stmt = apply_filters(
        select(func.count()).select_from(Game).outerjoin(Analysis, Analysis.game_id == Game.id), f
    )
    total = int(await session.scalar(count_stmt) or 0)
    return [to_list_item(g, acc) for g, acc in rows], total


def _common(game: Game, accuracy: float | None) -> dict:
    user_white = game.user_color == "w"
    return {
        "id": game.id,
        "account_id": game.account_id,
        "platform": game.platform,
        "platform_game_id": game.platform_game_id,
        "url": game.url,
        "white": game.white,
        "black": game.black,
        "white_rating": game.white_rating,
        "black_rating": game.black_rating,
        "user_color": game.user_color,
        "result": game.result,
        "user_result": game.user_result,
        "termination": game.termination,
        "time_class": game.time_class,
        "time_control": game.time_control,
        "rated": game.rated,
        "played_at": game.played_at,
        "eco": game.eco,
        "opening_name": game.opening_name,
        "ply_count": game.ply_count,
        "analysis_status": game.analysis_status,
        "accuracy": accuracy,
        "opponent": game.black if user_white else game.white,
        "opponent_rating": game.black_rating if user_white else game.white_rating,
        "user_rating": game.white_rating if user_white else game.black_rating,
    }


def to_list_item(game: Game, accuracy: float | None) -> GameListItem:
    return GameListItem(**_common(game, accuracy))


def to_game_out(game: Game, accuracy: float | None) -> GameOut:
    return GameOut(
        **_common(game, accuracy),
        pgn=game.pgn,
        platform_accuracy_white=game.platform_accuracy_white,
        platform_accuracy_black=game.platform_accuracy_black,
        imported_at=game.imported_at,
    )
