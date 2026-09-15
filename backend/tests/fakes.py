"""Shared fakes for platform and engine access."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from pathlib import Path

from lca.platforms.base import NormalizedGame, PlatformError
from lca.platforms.chesscom import normalize_chesscom_game
from lca.platforms.lichess import normalize_lichess_game

from .services.fake_engine import FakeEngine

FIXTURES = Path(__file__).parent / "fixtures"


def chesscom_fixture_games() -> list[NormalizedGame]:
    raw = json.loads((FIXTURES / "chesscom_archive_2025_08.json").read_text())
    return [g for g in (normalize_chesscom_game(r) for r in raw["games"]) if g]


def lichess_fixture_games() -> list[NormalizedGame]:
    out = []
    for line in (FIXTURES / "lichess_games.ndjson").read_text().splitlines():
        if line.strip():
            g = normalize_lichess_game(json.loads(line))
            if g:
                out.append(g)
    return out


class FakePlatform:
    """Serves fixture games; `users` maps lowercase username -> canonical name."""

    def __init__(self, name: str, games: list[NormalizedGame], users: dict[str, str]):
        self.name = name
        self.games = games
        self.users = users
        self.closed = False
        self.fail_with: PlatformError | None = None

    async def validate_user(self, username: str) -> str | None:
        return self.users.get(username.lower())

    async def fetch_games(
        self, username: str, cursor: str | None, *, months: int | None = None
    ) -> AsyncIterator[tuple[NormalizedGame, str]]:
        if self.fail_with is not None:
            raise self.fail_with
        games = self.games if not months else self.games[-months:]
        for i, g in enumerate(games):
            yield g, f"c{i}"

    async def count_archives(self, username, cursor, months) -> int:
        return len(self.games if not months else self.games[-months:])

    async def aclose(self) -> None:
        self.closed = True


def fake_platform_factory(name: str, settings: dict[str, str]):
    if name == "chesscom":
        return FakePlatform("chesscom", chesscom_fixture_games(), {"hikaru": "Hikaru"})
    return FakePlatform("lichess", lichess_fixture_games(), {"drnykterstein": "DrNykterstein"})


class FakeEngineProvider:
    def __init__(self, *_args, **_kwargs):
        self.engine = FakeEngine()
        self.invalidated: list[set[str] | None] = []

    async def get(self):
        return self.engine

    async def invalidate(self, changed_keys=None):
        self.invalidated.append(changed_keys)

    async def close(self):
        return None
