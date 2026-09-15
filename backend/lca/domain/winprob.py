"""Centipawn / mate evaluation to win probability (0..100)."""

from __future__ import annotations

import math

import chess

from .types import Eval

# Lichess' fitted coefficient for cp -> win expectancy.
_K = 0.00368208


def win_percent_white(ev: Eval) -> float:
    if ev.mate is not None:
        if ev.mate > 0:
            return 100.0
        if ev.mate < 0:
            return 0.0
        return 50.0
    cp = max(-10_000, min(10_000, ev.cp or 0))
    return 50.0 + 50.0 * (2.0 / (1.0 + math.exp(-_K * cp)) - 1.0)


def win_percent(ev: Eval, mover: chess.Color) -> float:
    w = win_percent_white(ev)
    return w if mover == chess.WHITE else 100.0 - w
