"""Move and game accuracy (Lichess' published formula)."""

from __future__ import annotations

import math
from statistics import pstdev


def move_accuracy(win_before: float, win_after: float) -> float:
    diff = max(0.0, win_before - win_after)
    acc = 103.1668 * math.exp(-0.04354 * diff) - 3.1669
    return round(max(0.0, min(100.0, acc)), 2)


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def game_accuracy(win_percents: list[float], move_accuracies: list[float]) -> float:
    """Combine per-move accuracies for one colour.

    `win_percents` is the win% (that colour's POV) at every position that colour had to
    move from, plus the resulting positions — used only to weight volatile phases more.
    Returns the mean of a volatility-weighted mean and a harmonic mean.
    """
    n = len(move_accuracies)
    if n == 0:
        return 100.0
    window = int(_clamp(len(win_percents) // 10, 2, 8))
    weights: list[float] = []
    for k in range(n):
        lo = max(0, k - window + 1)
        sample = win_percents[lo : k + 2] if len(win_percents) > k + 1 else win_percents[lo:]
        vol = pstdev(sample) if len(sample) >= 2 else 0.0
        weights.append(_clamp(vol, 0.5, 12.0))
    weighted = sum(a * w for a, w in zip(move_accuracies, weights, strict=True)) / sum(weights)
    harmonic = n / sum(1.0 / max(a, 0.01) for a in move_accuracies)
    return round((weighted + harmonic) / 2.0, 2)
