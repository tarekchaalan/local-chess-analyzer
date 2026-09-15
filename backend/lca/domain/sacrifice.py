"""Static exchange evaluation and sacrifice detection.

Uses legal-move generation on scratch boards, so pins and x-ray attackers are handled
without a dedicated attack model.
"""

from __future__ import annotations

import chess

PIECE_VALUES: dict[chess.PieceType, int] = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}

_MIN_SACRIFICE = 2  # exchange sac (5-3) and bishop-for-pawn (3-1) count; pawn sacs don't


def _value(board: chess.Board, square: chess.Square) -> int:
    piece = board.piece_at(square)
    return PIECE_VALUES[piece.piece_type] if piece else 0


def see(board: chess.Board, square: chess.Square) -> int:
    """Net material the side to move gains by starting a capture sequence on `square`.

    Never negative: a side simply declines to capture if it would lose material.
    """
    target = board.piece_at(square)
    if target is None or target.color == board.turn:
        return 0
    captures = list(board.generate_legal_captures(to_mask=chess.BB_SQUARES[square]))
    if not captures:
        return 0
    # Least valuable attacker first (kings last, since they are 0 but only legal if safe).
    captures.sort(key=lambda m: (_value(board, m.from_square) == 0, _value(board, m.from_square)))
    move = captures[0]
    gained = PIECE_VALUES[target.piece_type]
    scratch = board.copy(stack=False)
    scratch.push(move)
    return max(0, gained - see(scratch, square))


def en_prise(board: chess.Board, square: chess.Square) -> bool:
    """True if the side to move can win material by capturing on `square`."""
    return see(board, square) > 0


def _opponent_view(board: chess.Board) -> chess.Board | None:
    """The same position with the other side to move, or None if that is illegal (check)."""
    if board.is_check():
        return None
    flipped = board.copy(stack=False)
    flipped.push(chess.Move.null())
    return flipped


def is_piece_sacrifice(before: chess.Board, move: chess.Move) -> bool:
    """A non-pawn piece of the mover ends up en prise (net of what the move captured).

    Only pieces that were not already en prise before the move count, unless it is the
    moved piece itself.
    """
    mover = before.turn
    captured = 0
    if before.is_en_passant(move):
        captured = 1
    else:
        captured = _value(before, move.to_square)

    already_hanging: set[chess.Square] = set()
    opp_before = _opponent_view(before)
    if opp_before is not None:
        for sq in chess.SquareSet(before.occupied_co[mover]):
            if _value(before, sq) >= 3 and en_prise(opp_before, sq):
                already_hanging.add(sq)

    after = before.copy(stack=False)
    after.push(move)
    worst_loss = 0
    for sq in chess.SquareSet(after.occupied_co[mover]):
        if _value(after, sq) < 3:
            continue
        if sq != move.to_square and sq in already_hanging:
            continue
        worst_loss = max(worst_loss, see(after, sq))
    return worst_loss - captured >= _MIN_SACRIFICE


def is_simple_recapture(
    before: chess.Board, move: chess.Move, prev_move: chess.Move | None
) -> bool:
    """The move captures on the square the opponent just captured on."""
    if prev_move is None or not before.is_capture(move):
        return False
    if move.to_square != prev_move.to_square:
        return False
    # Was the previous move itself a capture? Check by undoing it on a copy.
    if not before.move_stack:
        return False
    scratch = before.copy()
    last = scratch.pop()
    return last == prev_move and scratch.is_capture(prev_move)
