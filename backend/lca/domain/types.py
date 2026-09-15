"""Small value types shared across the pure domain modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import chess
import chess.engine


@dataclass(frozen=True, slots=True)
class Eval:
    """Engine evaluation from White's point of view. Exactly one of cp/mate is set.

    mate > 0: White mates in N. mate < 0: Black mates in N. mate == 0: terminal (used
    for a checkmated position; win% treats it as neutral, callers map it themselves).
    """

    cp: int | None = None
    mate: int | None = None

    def __post_init__(self) -> None:
        if (self.cp is None) == (self.mate is None):
            raise ValueError("Eval needs exactly one of cp or mate")

    @property
    def is_mate(self) -> bool:
        return self.mate is not None

    def to_json(self) -> dict[str, int]:
        return {"mate": self.mate} if self.mate is not None else {"cp": self.cp or 0}

    @staticmethod
    def from_json(d: dict[str, Any]) -> Eval:
        if "mate" in d and d["mate"] is not None:
            return Eval(mate=int(d["mate"]))
        return Eval(cp=int(d.get("cp") or 0))

    @staticmethod
    def from_score(score: chess.engine.PovScore) -> Eval:
        w = score.white()
        m = w.mate()
        if m is not None:
            return Eval(mate=m)
        return Eval(cp=int(w.score() or 0))

    @staticmethod
    def terminal(board: chess.Board) -> Eval:
        """Eval of a finished position: mate 0 sign-encoded toward the winner, else 0 cp."""
        if board.is_checkmate():
            # Side to move is mated. Encode as a mate for the other side "in 0".
            return Eval(mate=-1 if board.turn == chess.WHITE else 1)
        return Eval(cp=0)
