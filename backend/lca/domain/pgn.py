"""PGN parsing helpers: headers, clocks, and platform vocabulary normalization."""

from __future__ import annotations

import io
from collections.abc import Mapping
from datetime import UTC, datetime

import chess.pgn

TIME_CLASSES = ("bullet", "blitz", "rapid", "classical", "daily")

_TIME_CLASS_MAP: dict[str, dict[str, str]] = {
    "lichess": {
        "ultrabullet": "bullet",
        "bullet": "bullet",
        "blitz": "blitz",
        "rapid": "rapid",
        "classical": "classical",
        "correspondence": "daily",
    },
    "chesscom": {
        "bullet": "bullet",
        "blitz": "blitz",
        "rapid": "rapid",
        "daily": "daily",
    },
}


def parse_game(pgn: str) -> chess.pgn.Game:
    game = chess.pgn.read_game(io.StringIO(pgn or ""))
    if game is None or game.next() is None:
        raise ValueError("invalid_pgn")
    return game


def _format_clock(seconds: float) -> str:
    total = int(seconds)
    frac = round(seconds - total, 1)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    base = f"{h}:{m:02d}:{s:02d}"
    if frac >= 0.1:
        base += f".{int(frac * 10)}"
    return base


def clocks_by_ply(game: chess.pgn.Game) -> list[str | None]:
    """Remaining clock after each ply (index = ply - 1), as `H:MM:SS[.d]`, or None."""
    out: list[str | None] = []
    node = game
    while node.next() is not None:
        node = node.next()
        clk = node.clock()
        out.append(_format_clock(clk) if clk is not None else None)
    return out


def normalize_time_class(platform: str, raw: str | None) -> str:
    table = _TIME_CLASS_MAP.get(platform, {})
    return table.get((raw or "").lower(), "blitz")


def result_for(user_color: str, result: str) -> str:
    if result == "1/2-1/2":
        return "draw"
    white_won = result == "1-0"
    user_is_white = user_color == "w"
    return "win" if white_won == user_is_white else "loss"


def played_at_from_headers(headers: Mapping[str, str]) -> datetime | None:
    date = headers.get("UTCDate") or headers.get("Date") or ""
    time = headers.get("UTCTime") or headers.get("StartTime") or "00:00:00"
    date = date.replace("-", ".")
    if "?" in date or not date:
        return None
    try:
        return datetime.strptime(f"{date} {time}", "%Y.%m.%d %H:%M:%S").replace(tzinfo=UTC)
    except ValueError:
        return None
