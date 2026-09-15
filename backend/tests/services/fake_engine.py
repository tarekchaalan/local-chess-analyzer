"""A deterministic engine stand-in: material-count evals, captures preferred."""

from __future__ import annotations

from collections.abc import Callable

import chess

from lca.domain.sacrifice import PIECE_VALUES
from lca.domain.types import Eval
from lca.services.engine import EngineLine

Scorer = Callable[[chess.Board], int]


def material_cp(board: chess.Board) -> int:
    total = 0
    for piece in board.piece_map().values():
        v = PIECE_VALUES[piece.piece_type] * 100
        total += v if piece.color == chess.WHITE else -v
    return total


class FakeEngine:
    name = "fake-engine 1.0"

    def __init__(self, scorer: Scorer = material_cp, *, depth: int = 10, time_ms: int = 0):
        self.scorer = scorer
        self.depth = depth
        self.time_ms = time_ms
        self.threads = 1
        self.hash_mb = 16
        self.calls = 0

    async def analyse(self, board: chess.Board, *, multipv: int = 2) -> list[EngineLine]:
        self.calls += 1
        if board.is_game_over():
            return []
        scored: list[tuple[int, chess.Move]] = []
        for mv in board.legal_moves:
            nb = board.copy(stack=False)
            nb.push(mv)
            if nb.is_checkmate():
                cp = 100_000 if board.turn == chess.WHITE else -100_000
            else:
                cp = self.scorer(nb)
            scored.append((cp, mv))
        # Best for White is max cp; for Black min cp.
        scored.sort(key=lambda t: (t[0], t[1].uci()), reverse=board.turn == chess.WHITE)
        lines: list[EngineLine] = []
        for cp, mv in scored[:multipv]:
            if abs(cp) >= 100_000:
                ev = Eval(mate=1 if cp > 0 else -1)
            else:
                ev = Eval(cp=cp)
            lines.append(EngineLine(move=mv, eval=ev, pv=[mv]))
        return lines

    async def close(self) -> None:
        return None
