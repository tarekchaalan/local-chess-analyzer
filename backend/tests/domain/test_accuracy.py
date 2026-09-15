import pytest

from lca.domain.accuracy import game_accuracy, move_accuracy


def test_no_loss_is_perfect():
    assert move_accuracy(50, 50) == 100.0


def test_gain_is_capped_at_100():
    assert move_accuracy(50, 60) == 100.0


def test_ten_point_drop():
    assert move_accuracy(50, 40) == pytest.approx(63.5, abs=0.5)


def test_huge_drop_floors_at_zero():
    assert move_accuracy(90, 5) == 0.0


def test_game_accuracy_all_perfect():
    assert game_accuracy([50, 50, 50, 50], [100, 100, 100]) == 100.0


def test_game_accuracy_mixed_is_between_means():
    acc = game_accuracy([50, 50, 50], [100, 0])
    assert 25 <= acc <= 50


def test_game_accuracy_empty():
    assert game_accuracy([], []) == 100.0
