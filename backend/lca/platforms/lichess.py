"""Lichess API client (https://lichess.org/api)."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import httpx

from ..domain.pgn import normalize_time_class
from .base import USER_AGENT, NormalizedGame, PlatformError

BASE_URL = "https://lichess.org"
PERF_TYPES = "ultraBullet,bullet,blitz,rapid,classical,correspondence"

_TERMINATION = {
    "mate": "checkmate",
    "resign": "resignation",
    "outoftime": "timeout",
    "timeout": "timeout",
    "draw": "draw",
    "stalemate": "stalemate",
    "cheat": "cheat detected",
    "variantEnd": "variant end",
    "unknownFinish": None,
}
_SKIP_STATUSES = {"created", "started", "aborted", "noStart"}


def normalize_lichess_game(raw: dict) -> NormalizedGame | None:
    if raw.get("variant") != "standard":
        return None
    if raw.get("status") in _SKIP_STATUSES:
        return None
    if raw.get("initialFen"):
        return None
    players = raw.get("players", {})
    w_user = players.get("white", {}).get("user")
    b_user = players.get("black", {}).get("user")
    if not w_user or not b_user:
        return None
    pgn = raw.get("pgn") or ""
    if not pgn:
        return None
    winner = raw.get("winner")
    result = "1-0" if winner == "white" else "0-1" if winner == "black" else "1/2-1/2"
    clock = raw.get("clock")
    if clock:
        time_control = f"{clock.get('initial', 0)}+{clock.get('increment', 0)}"
    elif raw.get("daysPerTurn"):
        time_control = f"{raw['daysPerTurn']}d"
    else:
        time_control = None
    opening = raw.get("opening") or {}
    created = raw.get("createdAt") or 0
    return NormalizedGame(
        platform="lichess",
        platform_game_id=raw["id"],
        url=f"{BASE_URL}/{raw['id']}",
        pgn=pgn,
        white=w_user.get("name", "?"),
        black=b_user.get("name", "?"),
        white_rating=players.get("white", {}).get("rating"),
        black_rating=players.get("black", {}).get("rating"),
        result=result,
        termination=_TERMINATION.get(raw.get("status", ""), raw.get("status")),
        time_class=normalize_time_class("lichess", raw.get("speed")),
        time_control=time_control,
        rated=bool(raw.get("rated", True)),
        played_at=datetime.fromtimestamp(created / 1000, tz=UTC),
        eco=opening.get("eco"),
        opening_name=opening.get("name"),
    )


class LichessPlatform:
    name = "lichess"

    def __init__(self, client: httpx.AsyncClient | None = None, token: str | None = None):
        headers = {"User-Agent": USER_AGENT}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = client or httpx.AsyncClient(timeout=60.0)
        self._client.headers.update(headers)

    async def aclose(self) -> None:
        await self._client.aclose()

    @staticmethod
    def _raise_for(r: httpx.Response) -> None:
        if r.status_code == 404:
            raise PlatformError("user_not_found", "Lichess user not found")
        if r.status_code == 429:
            retry = float(r.headers.get("Retry-After", "60"))
            raise PlatformError("rate_limited", "Lichess rate limit", retry_after=retry)
        if r.status_code >= 400:
            raise PlatformError("upstream_error", f"Lichess returned {r.status_code}")

    async def validate_user(self, username: str) -> str | None:
        try:
            r = await self._client.get(f"{BASE_URL}/api/user/{username}")
        except httpx.HTTPError as e:
            raise PlatformError("network_error", f"Lichess request failed: {e}") from e
        if r.status_code == 404:
            return None
        self._raise_for(r)
        return r.json().get("username") or username

    async def fetch_games(
        self, username: str, cursor: str | None, *, months: int | None = None
    ) -> AsyncIterator[tuple[NormalizedGame, str]]:
        params: dict[str, str] = {
            "pgnInJson": "true",
            "clocks": "true",
            "opening": "true",
            "perfType": PERF_TYPES,
            "sort": "dateAsc",
        }
        if cursor:
            params["since"] = cursor
        if months:
            since_ms = int((datetime.now(tz=UTC).timestamp() - months * 30 * 86400) * 1000)
            params["since"] = str(max(int(cursor or 0), since_ms))
        max_created = int(cursor or 0)
        try:
            async with self._client.stream(
                "GET",
                f"{BASE_URL}/api/games/user/{username}",
                params=params,
                headers={"Accept": "application/x-ndjson"},
            ) as r:
                self._raise_for(r)
                async for line in r.aiter_lines():
                    if not line.strip():
                        continue
                    raw = json.loads(line)
                    game = normalize_lichess_game(raw)
                    max_created = max(max_created, int(raw.get("createdAt") or 0) + 1)
                    if game is not None:
                        yield game, str(max_created)
        except httpx.HTTPError as e:
            raise PlatformError("network_error", f"Lichess request failed: {e}") from e
