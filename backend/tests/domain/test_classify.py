import chess
import pytest

from lca.domain.classify import LABELS, MoveContext, classify


def _ctx(fen: str, uci: str, *, best: str | None = None, **kw) -> MoveContext:
    board = chess.Board(fen)
    move = chess.Move.from_uci(uci)
    defaults = dict(
        win_before=50.0,
        win_after=50.0,
        second_win=None,
        in_book=False,
        best_is_mate=False,
        mover_mated_before=False,
        prev_classification=None,
        prev_move=None,
    )
    defaults.update(kw)
    return MoveContext(
        board_before=board,
        move=move,
        best_move=chess.Move.from_uci(best) if best else move,
        **defaults,
    )


START = chess.STARTING_FEN
GREEK_GIFT = "5rk1/5ppp/8/8/8/3B1N2/8/3QK3 w - - 0 1"


def test_labels_are_exactly_the_spec_set():
    assert LABELS == (
        "book", "forced", "brilliant", "great", "best", "miss",
        "excellent", "good", "inaccuracy", "mistake", "blunder",
    )  # fmt: skip


def test_book():
    assert classify(_ctx(START, "e2e4", in_book=True)) == "book"


def test_forced_single_legal_move():
    # White king on g1 in check from a rook on a1; pawns block g2/h2, so only Kf2.
    fen = "k7/8/8/8/8/8/6PP/r5K1 w - - 0 1"
    board = chess.Board(fen)
    legal = list(board.legal_moves)
    assert len(legal) == 1
    assert classify(_ctx(fen, legal[0].uci(), best="g1f2")) == "forced"


def test_brilliant_greek_gift():
    ctx = _ctx(GREEK_GIFT, "d3h7", win_before=55, win_after=60)
    assert classify(ctx) == "brilliant"


def test_brilliant_requires_near_best():
    ctx = _ctx(GREEK_GIFT, "d3h7", best="f3g5", win_before=55, win_after=50)
    assert classify(ctx) != "brilliant"


def test_brilliant_blocked_when_already_crushing():
    ctx = _ctx(GREEK_GIFT, "d3h7", win_before=95, win_after=96)
    assert classify(ctx) == "best"


def test_brilliant_blocked_when_losing_after():
    ctx = _ctx(GREEK_GIFT, "d3h7", win_before=32, win_after=30)
    assert classify(ctx) == "best"


def test_great_only_move():
    ctx = _ctx(START, "e2e4", win_before=52, win_after=52, second_win=35)
    assert classify(ctx) == "great"


def test_great_requires_played_equals_best():
    ctx = _ctx(START, "d2d4", best="e2e4", win_before=52, win_after=52, second_win=35)
    assert classify(ctx) == "best"


def test_great_not_for_simple_recapture():
    board = chess.Board()
    for san in ("e4", "d5", "exd5"):
        board.push_san(san)
    ctx = MoveContext(
        board_before=board,
        move=chess.Move.from_uci("d8d5"),
        best_move=chess.Move.from_uci("d8d5"),
        win_before=50,
        win_after=50,
        second_win=35,
        in_book=False,
        best_is_mate=False,
        mover_mated_before=False,
        prev_classification=None,
        prev_move=board.peek(),
    )
    assert classify(ctx) == "best"


def test_great_blocked_when_lost_anyway():
    ctx = _ctx(START, "e2e4", win_before=15, win_after=15, second_win=3)
    assert classify(ctx) == "best"


def test_best_when_eval_did_not_drop_even_if_not_pv1():
    ctx = _ctx(START, "d2d4", best="e2e4", win_before=50, win_after=50)
    assert classify(ctx) == "best"


def test_miss_after_opponent_blunder():
    ctx = _ctx(
        START, "d2d4", best="e2e4", win_before=80, win_after=62, prev_classification="blunder"
    )
    assert classify(ctx) == "miss"


def test_miss_when_mate_was_available():
    ctx = _ctx(START, "d2d4", best="e2e4", win_before=100, win_after=85, best_is_mate=True)
    assert classify(ctx) == "miss"


def test_miss_not_when_position_collapses():
    ctx = _ctx(
        START, "d2d4", best="e2e4", win_before=80, win_after=30, prev_classification="blunder"
    )
    assert classify(ctx) == "blunder"


@pytest.mark.parametrize(
    ("after", "label"),
    [(49, "excellent"), (46, "good"), (42, "inaccuracy"), (35, "mistake"), (20, "blunder")],
)
def test_thresholds(after, label):
    ctx = _ctx(START, "d2d4", best="e2e4", win_before=50, win_after=after)
    assert classify(ctx) == label
