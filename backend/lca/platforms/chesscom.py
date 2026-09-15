"""chess.com public API client (https://api.chess.com/pub)."""

from __future__ import annotations

import re
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import httpx

from ..domain.pgn import normalize_time_class
from .base import USER_AGENT, NormalizedGame, PlatformError

BASE_URL = "https://api.chess.com/pub"
STANDARD_START = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

_TERMINATION = {
    "checkmated": "checkmate",
    "resigned": "resignation",
    "timeout": "timeout",
    "abandoned": "abandoned",
    "stalemate": "stalemate",
    "repetition": "repetition",
    "agreed": "agreement",
    "insufficient": "insufficient material",
    "50move": "50-move rule",
    "timevsinsufficient": "timeout vs insufficient material",
    "lose": "loss",
}

_ECO_HEADER = re.compile(r'\[ECO "([A-E]\d\d)"\]')
_MONTH_RE = re.compile(r"/(\d{4})/(\d{2})$")


def _month_of(archive_url: str) -> str:
    m = _MONTH_RE.search(archive_url)
    return f"{m.group(1)}/{m.group(2)}" if m else archive_url


def _opening_name_from_url(url: str | None) -> str | None:
    if not url:
        return None
    slug = url.rstrip("/").split("/")[-1]
    # Cut at the first move token: "-1.e4", "-1...d5", "...4.Nf3", "-2.Nf3".
    slug = re.split(r"(?:-|\.\.\.)\d+\.{1,3}", slug)[0]
    name = slug.replace("-", " ").strip()
    return name or None


def normalize_chesscom_game(raw: dict) -> NormalizedGame | None:
    if raw.get("rules") != "chess":
        return None
    if raw.get("initial_setup") and raw["initial_setup"] != STANDARD_START:
        return None
    pgn = raw.get("pgn") or ""
    if not pgn:
        return None
    white, black = raw.get("white", {}), raw.get("black", {})
    w_res, b_res = white.get("result"), black.get("result")
    if w_res == "win":
        result, loser = "1-0", b_res
    elif b_res == "win":
        result, loser = "0-1", w_res
    else:
        result, loser = "1/2-1/2", w_res
    end_time = raw.get("end_time")
    played_at = datetime.fromtimestamp(end_time, tz=UTC) if end_time else datetime.now(tz=UTC)
    eco_match = _ECO_HEADER.search(pgn)
    acc = raw.get("accuracies") or {}
    return NormalizedGame(
        platform="chesscom",
        platform_game_id=raw.get("uuid") or (raw.get("url") or "").rsplit("/", 1)[-1],
        url=raw.get("url"),
        pgn=pgn,
        white=white.get("username", "?"),
        black=black.get("username", "?"),
        white_rating=white.get("rating"),
        black_rating=black.get("rating"),
        result=result,
        termination=_TERMINATION.get(loser or "", loser),
        time_class=normalize_time_class("chesscom", raw.get("time_class")),
        time_control=raw.get("time_control"),
        rated=bool(raw.get("rated", True)),
        played_at=played_at,
        eco=eco_match.group(1) if eco_match else None,
        opening_name=_opening_name_from_url(raw.get("eco")),
        platform_accuracy_white=acc.get("white"),
        platform_accuracy_black=acc.get("black"),
    )


class ChessComPlatform:
    name = "chesscom"

    def __init__(self, client: httpx.AsyncClient | None = None):
        self._client = client or httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self._client.headers["User-Agent"] = USER_AGENT

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _get_json(self, url: str) -> dict:
        try:
            r = await self._client.get(url)
        except httpx.HTTPError as e:
            raise PlatformError("network_error", f"chess.com request failed: {e}") from e
        if r.status_code == 404:
            raise PlatformError("user_not_found", "chess.com user not found")
        if r.status_code == 429:
            retry = float(r.headers.get("Retry-After", "10"))
            raise PlatformError("rate_limited", "chess.com rate limit", retry_after=retry)
        if r.status_code >= 400:
            raise PlatformError("upstream_error", f"chess.com returned {r.status_code}")
        return r.json()

    async def validate_user(self, username: str) -> str | None:
        try:
            data = await self._get_json(f"{BASE_URL}/player/{username.lower()}")
        except PlatformError as e:
            if e.code == "user_not_found":
                return None
            raise
        url = data.get("url") or ""
        display = url.rstrip("/").split("/")[-1] if url else ""
        return display or data.get("username") or username

    async def fetch_games(
        self, username: str, cursor: str | None, *, months: int | None = None
    ) -> AsyncIterator[tuple[NormalizedGame, str]]:
        data = await self._get_json(f"{BASE_URL}/player/{username.lower()}/games/archives")
        archives: list[str] = data.get("archives", [])
        if months:
            archives = archives[-months:]
        if cursor:
            archives = [a for a in archives if _month_of(a) >= cursor]
        for archive in archives:
            month = _month_of(archive)
            payload = await self._get_json(archive)
            for raw in payload.get("games", []):
                game = normalize_chesscom_game(raw)
                if game is not None:
                    yield game, month

    async def count_archives(self, username: str, cursor: str | None, months: int | None) -> int:
        data = await self._get_json(f"{BASE_URL}/player/{username.lower()}/games/archives")
        archives: list[str] = data.get("archives", [])
        if months:
            archives = archives[-months:]
        if cursor:
            archives = [a for a in archives if _month_of(a) >= cursor]
        return len(archives)
