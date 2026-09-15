"""Common contract for game sources."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

PLATFORMS = ("chesscom", "lichess")

USER_AGENT = "LocalChessAnalyzer/2.0 (+https://github.com/tarekchaalan/local-chess-analyzer)"


@dataclass(slots=True)
class NormalizedGame:
    platform: str
    platform_game_id: str
    url: str | None
    pgn: str
    white: str
    black: str
    white_rating: int | None
    black_rating: int | None
    result: str  # 1-0 | 0-1 | 1/2-1/2
    termination: str | None
    time_class: str
    time_control: str | None
    rated: bool
    played_at: datetime
    eco: str | None = None
    opening_name: str | None = None
    platform_accuracy_white: float | None = None
    platform_accuracy_black: float | None = None


class PlatformError(Exception):
    def __init__(self, code: str, message: str, *, retry_after: float | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.retry_after = retry_after


class Platform(Protocol):
    name: str

    async def validate_user(self, username: str) -> str | None:
        """Canonical username if the user exists, else None."""

    def fetch_games(
        self, username: str, cursor: str | None, *, months: int | None = None
    ) -> AsyncIterator[tuple[NormalizedGame, str]]:
        """Yield (game, cursor_after_this_game). Games arrive oldest-first where possible."""

    async def aclose(self) -> None: ...


def get_platform(name: str, *, lichess_token: str | None = None) -> Platform:
    if name == "chesscom":
        from .chesscom import ChessComPlatform

        return ChessComPlatform()
    if name == "lichess":
        from .lichess import LichessPlatform

        return LichessPlatform(token=lichess_token or None)
    raise PlatformError("unknown_platform", f"Unknown platform: {name}")
