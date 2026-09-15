from datetime import UTC
from pathlib import Path

import pytest

from lca.domain.pgn import (
    clocks_by_ply,
    normalize_time_class,
    parse_game,
    played_at_from_headers,
    result_for,
)

FIXTURES = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def sample_pgn() -> str:
    return (FIXTURES / "sample_chesscom.pgn").read_text()


def test_parse_game_reads_headers_and_moves(sample_pgn):
    game = parse_game(sample_pgn)
    assert game.headers["White"] == "GHANDEEVAM2003"
    assert len(list(game.mainline_moves())) > 20


def test_parse_game_rejects_garbage():
    with pytest.raises(ValueError, match="invalid_pgn"):
        parse_game("")
    with pytest.raises(ValueError, match="invalid_pgn"):
        parse_game('[Event "x"]\n\n*')


def test_clocks_by_ply(sample_pgn):
    clocks = clocks_by_ply(parse_game(sample_pgn))
    assert clocks[0] == "0:09:57.7"
    assert clocks[1] == "0:09:57.7"
    assert clocks[2] == "0:09:56.1"
    assert all(c is None or ":" in c for c in clocks)


def test_clocks_without_comments():
    game = parse_game("1. e4 e5 2. Nf3 *")
    assert clocks_by_ply(game) == [None, None, None]


@pytest.mark.parametrize(
    ("platform", "raw", "expected"),
    [
        ("lichess", "ultraBullet", "bullet"),
        ("lichess", "bullet", "bullet"),
        ("lichess", "blitz", "blitz"),
        ("lichess", "rapid", "rapid"),
        ("lichess", "classical", "classical"),
        ("lichess", "correspondence", "daily"),
        ("chesscom", "daily", "daily"),
        ("chesscom", "bullet", "bullet"),
        ("chesscom", "weird", "blitz"),
    ],
)
def test_normalize_time_class(platform, raw, expected):
    assert normalize_time_class(platform, raw) == expected


def test_result_for():
    assert result_for("b", "0-1") == "win"
    assert result_for("w", "0-1") == "loss"
    assert result_for("w", "1/2-1/2") == "draw"
    assert result_for("b", "1-0") == "loss"


def test_played_at_from_headers():
    dt = played_at_from_headers({"UTCDate": "2025.08.01", "UTCTime": "13:01:35"})
    assert dt is not None and dt.tzinfo == UTC
    assert dt.isoformat() == "2025-08-01T13:01:35+00:00"
    assert played_at_from_headers({"Date": "2025.08.01"}).isoformat() == "2025-08-01T00:00:00+00:00"
    assert played_at_from_headers({"Date": "????.??.??"}) is None
