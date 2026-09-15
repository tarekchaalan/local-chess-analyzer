import chess
import pytest

from lca.domain.types import Eval
from lca.domain.winprob import win_percent, win_percent_white


def test_equal_position_is_fifty():
    assert win_percent_white(Eval(cp=0)) == pytest.approx(50.0)


def test_one_pawn_up_is_about_59():
    assert win_percent_white(Eval(cp=100)) == pytest.approx(59.1, abs=0.2)


def test_symmetry():
    assert win_percent_white(Eval(cp=-100)) == pytest.approx(100 - win_percent_white(Eval(cp=100)))


def test_mate_saturates():
    assert win_percent_white(Eval(mate=3)) == 100.0
    assert win_percent_white(Eval(mate=-1)) == 0.0


def test_mate_zero_means_side_to_move_is_mated_is_encoded_by_sign():
    # Eval(mate=0) is only produced for terminal checkmate; caller sets sign via helper.
    assert win_percent_white(Eval(mate=0)) == 50.0


def test_mover_perspective():
    assert win_percent(Eval(cp=100), chess.BLACK) == pytest.approx(40.9, abs=0.2)
    assert win_percent(Eval(cp=100), chess.WHITE) == pytest.approx(59.1, abs=0.2)


def test_eval_json_roundtrip():
    assert Eval(cp=35).to_json() == {"cp": 35}
    assert Eval(mate=-2).to_json() == {"mate": -2}
    assert Eval.from_json({"cp": 35}) == Eval(cp=35)
