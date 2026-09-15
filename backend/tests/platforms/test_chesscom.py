import httpx
import pytest

from lca.platforms.base import PlatformError
from lca.platforms.chesscom import ChessComPlatform, _opening_name_from_url


def _transport(fixtures, *, rate_limit=False):
    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        assert "User-Agent" in request.headers
        if rate_limit:
            return httpx.Response(429, headers={"Retry-After": "7"})
        if url.endswith("/player/hikaru"):
            return httpx.Response(200, content=(fixtures / "chesscom_player.json").read_bytes())
        if url.endswith("/player/nobody"):
            return httpx.Response(404, json={"message": "not found"})
        if url.endswith("/player/hikaru/games/archives"):
            return httpx.Response(200, content=(fixtures / "chesscom_archives.json").read_bytes())
        if url.endswith("/games/2025/08"):
            return httpx.Response(
                200, content=(fixtures / "chesscom_archive_2025_08.json").read_bytes()
            )
        if url.endswith("/games/2025/07"):
            return httpx.Response(200, json={"games": []})
        return httpx.Response(500)

    return httpx.MockTransport(handler)


@pytest.fixture
def platform(fixtures):
    return ChessComPlatform(client=httpx.AsyncClient(transport=_transport(fixtures)))


async def test_validate_user(platform):
    assert await platform.validate_user("HIKARU") == "Hikaru"
    assert await platform.validate_user("nobody") is None


async def test_fetch_filters_variants_and_maps_fields(platform):
    games = [g async for g in platform.fetch_games("hikaru", None)]
    assert len(games) == 4  # 5 in fixture, one is chess960
    game, cursor = games[0]
    assert cursor == "2025/08"
    assert game.platform == "chesscom"
    assert game.platform_game_id == "a754022b-6ed7-11f0-a782-67c26501000f"
    assert game.white == "GHANDEEVAM2003" and game.black == "Hikaru"
    assert game.result == "1-0"
    assert game.termination == "resignation"
    assert game.time_class == "rapid"
    assert game.time_control == "600"
    assert game.platform_accuracy_white == 91.6
    assert game.eco == "D06"
    assert game.opening_name == "Queens Gambit Declined Austrian Variation"
    assert game.played_at.isoformat() == "2025-08-01T13:14:34+00:00"
    assert "[%clk" in game.pgn


async def test_months_limits_archives(platform):
    games = [g async for g in platform.fetch_games("hikaru", None, months=1)]
    assert len(games) == 4
    assert await platform.count_archives("hikaru", None, 1) == 1


async def test_cursor_skips_older_archives(platform):
    assert await platform.count_archives("hikaru", "2025/08", None) == 1
    assert await platform.count_archives("hikaru", None, None) == 2


async def test_rate_limit_raises(fixtures):
    p = ChessComPlatform(client=httpx.AsyncClient(transport=_transport(fixtures, rate_limit=True)))
    with pytest.raises(PlatformError) as ei:
        await p.validate_user("hikaru")
    assert ei.value.code == "rate_limited" and ei.value.retry_after == 7


def test_opening_name_from_url():
    assert (
        _opening_name_from_url(
            "https://www.chess.com/openings/Sicilian-Defense-Najdorf-Variation-6.Bg5"
        )
        == "Sicilian Defense Najdorf Variation"
    )
    assert _opening_name_from_url(None) is None
