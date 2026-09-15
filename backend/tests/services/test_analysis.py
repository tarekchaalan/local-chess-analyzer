import pytest

from lca.domain.classify import LABELS
from lca.domain.openings import OpeningBook
from lca.services.analysis import AnalysisCancelled, analyze_game

from .fake_engine import FakeEngine

SCHOLARS_MATE = "1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7# 1-0"
BLUNDER_GAME = "1. e4 e5 2. Nf3 Nc6 3. Bc4 Nf6 4. Ng5 d5 5. exd5 Nxd5 6. Nxf7 Kxf7 *"


@pytest.fixture(scope="module")
def book():
    return OpeningBook.load()


async def test_report_shape(book):
    engine = FakeEngine()
    progress = []

    async def on_progress(done, total):
        progress.append((done, total))

    report = await analyze_game(SCHOLARS_MATE, engine, book, on_progress=on_progress)
    assert len(report.moves) == 7
    assert progress == [(i, 7) for i in range(1, 8)]
    assert report.engine_name == "fake-engine 1.0"
    assert set(report.counts) == {"w", "b"}
    assert set(report.counts["w"]) == set(LABELS)
    assert sum(report.counts["w"].values()) == 4
    assert sum(report.counts["b"].values()) == 3
    first = report.moves[0]
    for key in (
        "ply", "san", "uci", "color", "eval_before", "eval_after", "best", "second",
        "win_before", "win_after", "accuracy", "classification", "book", "clock",
    ):  # fmt: skip
        assert key in first
    assert first["san"] == "e4" and first["color"] == "w" and first["ply"] == 1
    assert first["best"]["line"]
    assert report.moves[-1]["eval_after"] == {"mate": 1}
    assert report.moves[-1]["win_after"] == 100.0
    assert 0 <= report.accuracy_white <= 100 and 0 <= report.accuracy_black <= 100


async def test_opening_detection(book):
    report = await analyze_game(SCHOLARS_MATE, FakeEngine(), book)
    assert report.book_plies >= 2
    assert report.opening_name is not None
    assert report.moves[0]["classification"] == "book"
    assert report.moves[0]["book"] is True


async def test_material_blunder_is_flagged(book):
    report = await analyze_game(BLUNDER_GAME, FakeEngine(), book)
    # 6. Nxf7?? loses the knight for a pawn in the material model.
    nxf7 = next(m for m in report.moves if m["san"] == "Nxf7")
    assert nxf7["classification"] in ("blunder", "mistake", "inaccuracy")
    kxf7 = next(m for m in report.moves if m["san"] == "Kxf7")
    assert kxf7["classification"] in ("best", "great", "excellent", "forced")


async def test_cancellation(book):
    calls = {"n": 0}

    def cancelled():
        calls["n"] += 1
        return calls["n"] > 2

    with pytest.raises(AnalysisCancelled):
        await analyze_game(SCHOLARS_MATE, FakeEngine(), book, is_cancelled=cancelled)


async def test_invalid_pgn(book):
    with pytest.raises(ValueError, match="invalid_pgn"):
        await analyze_game("garbage", FakeEngine(), book)
