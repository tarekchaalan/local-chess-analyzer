"""chess.com-standard move classification.

All win percentages are from the mover's point of view, 0..100.
"""

from __future__ import annotations

from dataclasses import dataclass

import chess

from .sacrifice import is_piece_sacrifice, is_simple_recapture

LABELS = (
    "book",
    "forced",
    "brilliant",
    "great",
    "best",
    "miss",
    "excellent",
    "good",
    "inaccuracy",
    "mistake",
    "blunder",
)

# Expected-points loss thresholds (in win%): 0.02 / 0.05 / 0.10 / 0.20.
EXCELLENT_MAX = 2.0
GOOD_MAX = 5.0
INACCURACY_MAX = 10.0
MISTAKE_MAX = 20.0

BRILLIANT_MAX_LOSS = 2.0
BRILLIANT_MIN_WIN_AFTER = 40.0
BRILLIANT_MAX_WIN_BEFORE = 90.0
GREAT_MIN_GAP = 10.0
GREAT_MIN_WIN_BEFORE = 30.0
GREAT_MAX_LEGAL_WHEN_IN_CHECK = 3  # escaping check with few options is not "finding" a move
MISS_MIN_LOSS = 10.0
MISS_MIN_WIN_AFTER = 50.0


@dataclass(slots=True)
class MoveContext:
    board_before: chess.Board
    move: chess.Move
    best_move: chess.Move | None
    win_before: float
    win_after: float
    second_win: float | None
    in_book: bool
    best_is_mate: bool
    mover_mated_before: bool
    prev_classification: str | None
    prev_move: chess.Move | None


def classify(ctx: MoveContext) -> str:
    if ctx.in_book:
        return "book"
    legal_count = ctx.board_before.legal_moves.count()
    if legal_count == 1:
        return "forced"

    loss = ctx.win_before - ctx.win_after
    is_pv1 = ctx.best_move is not None and ctx.move == ctx.best_move

    if (
        loss <= BRILLIANT_MAX_LOSS
        and ctx.win_after >= BRILLIANT_MIN_WIN_AFTER
        and ctx.win_before <= BRILLIANT_MAX_WIN_BEFORE
        and not ctx.mover_mated_before
        and is_piece_sacrifice(ctx.board_before, ctx.move)
    ):
        return "brilliant"

    if (
        is_pv1
        and ctx.second_win is not None
        and ctx.win_before - ctx.second_win >= GREAT_MIN_GAP
        and ctx.win_before >= GREAT_MIN_WIN_BEFORE
        and not (ctx.board_before.is_check() and legal_count <= GREAT_MAX_LEGAL_WHEN_IN_CHECK)
        and not is_simple_recapture(ctx.board_before, ctx.move, ctx.prev_move)
    ):
        return "great"

    if is_pv1 or loss <= 0:
        return "best"

    opportunity = ctx.prev_classification in ("mistake", "blunder") or ctx.best_is_mate
    if opportunity and loss >= MISS_MIN_LOSS and ctx.win_after >= MISS_MIN_WIN_AFTER:
        return "miss"

    if loss <= EXCELLENT_MAX:
        return "excellent"
    if loss <= GOOD_MAX:
        return "good"
    if loss <= INACCURACY_MAX:
        return "inaccuracy"
    if loss <= MISTAKE_MAX:
        return "mistake"
    return "blunder"
