import httpx
import pytest

from lca.platforms.base import PlatformError
from lca.platforms.lichess import LichessPlatform


def _transport(fixtures, *, rate_limit=False, capture: dict | None = None):
    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if capture is not None:
            capture["params"] = dict(request.url.params)
            capture["headers"] = dict(request.headers)
        if rate_limit:
            return httpx.Response(429, headers={"Retry-After": "42"})
        if "/api/user/DrNykterstein" in url:
            return httpx.Response(200, content=(fixtures / "lichess_user.json").read_bytes())
        if "/api/user/nobody" in url:
            return httpx.Response(404)
        if "/api/games/user/DrNykterstein" in url:
            return httpx.Response(200, content=(fixtures / "lichess_games.ndjson").read_bytes())
        return httpx.Response(500)

    return httpx.MockTransport(handler)


@pytest.fixture
def platform(fixtures):
    return LichessPlatform(client=httpx.AsyncClient(transport=_transport(fixtures)))


async def test_validate_user(platform):
    assert await platform.validate_user("DrNykterstein") == "DrNykterstein"
    assert await platform.validate_user("nobody") is None


async def test_fetch_filters_variants_and_maps_fields(platform):
    games = [g async for g in platform.fetch_games("DrNykterstein", None)]
    assert len(games) == 3  # fixture has 4, one chess960
    game, cursor = games[0]
    assert game.platform == "lichess"
    assert game.platform_game_id == "kAdOQKeh"
    assert game.url == "https://lichess.org/kAdOQKeh"
    assert game.white == "respects_55" and game.black == "DrNykterstein"
    assert game.result == "0-1"
    assert game.termination == "resignation"
    assert game.time_class == "blitz"
    assert game.time_control == "180+0"
    assert game.eco == "B02"
    assert game.opening_name == "Alekhine Defense: Sämisch Attack"
    assert game.played_at.year == 2026
    assert cursor == str(1775677143033 + 1)


async def test_cursor_is_monotonic(platform):
    cursors = [c async for _, c in platform.fetch_games("DrNykterstein", None)]
    assert cursors == sorted(cursors, key=int)


async def test_since_and_token_are_sent(fixtures):
    cap: dict = {}
    p = LichessPlatform(
        client=httpx.AsyncClient(transport=_transport(fixtures, capture=cap)), token="abc"
    )
    _ = [g async for g in p.fetch_games("DrNykterstein", "123")]
    assert cap["params"]["since"] == "123"
    assert cap["params"]["pgnInJson"] == "true"
    assert cap["headers"]["accept"] == "application/x-ndjson"
    assert cap["headers"]["authorization"] == "Bearer abc"


async def test_rate_limit(fixtures):
    p = LichessPlatform(client=httpx.AsyncClient(transport=_transport(fixtures, rate_limit=True)))
    with pytest.raises(PlatformError) as ei:
        _ = [g async for g in p.fetch_games("DrNykterstein", None)]
    assert ei.value.code == "rate_limited" and ei.value.retry_after == 42
