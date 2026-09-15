"""Full-game analysis: engine evaluations -> classified, scored move records."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

import chess

from ..domain.accuracy import game_accuracy, move_accuracy
from ..domain.classify import LABELS, MoveContext, classify
from ..domain.openings import Opening, OpeningBook
from ..domain.pgn import clocks_by_ply, parse_game
from ..domain.types import Eval
from ..domain.winprob import win_percent, win_percent_white
from .engine import EngineLine, EngineProtocol

ProgressCallback = Callable[[int, int], Awaitable[None]]
CancelCheck = Callable[[], bool]


class AnalysisCancelled(Exception):
    pass


@dataclass(slots=True)
class Report:
    engine_name: str
    depth: int
    time_ms: int
    multipv: int
    threads: int
    hash_mb: int
    accuracy_white: float
    accuracy_black: float
    opening_eco: str | None
    opening_name: str | None
    book_plies: int
    counts: dict[str, dict[str, int]]
    moves: list[dict[str, Any]] = field(default_factory=list)


def _san_line(board: chess.Board, pv: list[chess.Move], limit: int = 8) -> list[str]:
    scratch = board.copy(stack=False)
    out: list[str] = []
    for mv in pv[:limit]:
        if mv not in scratch.legal_moves:
            break
        out.append(scratch.san(mv))
        scratch.push(mv)
    return out


def _line_json(board: chess.Board, line: EngineLine | None, *, with_line: bool) -> dict | None:
    if line is None:
        return None
    d: dict[str, Any] = {
        "uci": line.move.uci(),
        "san": board.san(line.move) if line.move in board.legal_moves else line.move.uci(),
        "eval": line.eval.to_json(),
    }
    if with_line:
        d["line"] = _san_line(board, line.pv)
    return d


def _empty_counts() -> dict[str, dict[str, int]]:
    return {"w": dict.fromkeys(LABELS, 0), "b": dict.fromkeys(LABELS, 0)}


async def analyze_game(
    pgn: str,
    engine: EngineProtocol,
    book: OpeningBook,
    *,
    on_progress: ProgressCallback | None = None,
    is_cancelled: CancelCheck | None = None,
) -> Report:
    game = parse_game(pgn)
    clocks = clocks_by_ply(game)
    moves = list(game.mainline_moves())
    total = len(moves)

    board = game.board()
    lines = await engine.analyse(board, multipv=2)

    in_book = True
    book_plies = 0
    opening: Opening | None = None
    records: list[dict[str, Any]] = []
    counts = _empty_counts()
    position_evals: list[Eval] = [lines[0].eval if lines else Eval(cp=0)]
    accuracies: dict[chess.Color, list[float]] = {chess.WHITE: [], chess.BLACK: []}
    prev_classification: str | None = None
    prev_move: chess.Move | None = None

    for i, move in enumerate(moves):
        if is_cancelled and is_cancelled():
            raise AnalysisCancelled()

        mover = board.turn
        before = board.copy()
        best = lines[0] if lines else None
        second = lines[1] if len(lines) > 1 else None
        eval_before = best.eval if best else Eval(cp=0)
        mover_mated_before = eval_before.is_mate and win_percent(eval_before, mover) == 0.0
        best_is_mate = eval_before.is_mate and win_percent(eval_before, mover) == 100.0

        san = board.san(move)
        board.push(move)

        if in_book and book.is_book(board):
            book_plies = i + 1
            opening = book.lookup(board.epd()) or opening
        else:
            in_book = False

        if board.is_game_over():
            eval_after = Eval.terminal(board)
            lines = []
        else:
            lines = await engine.analyse(board, multipv=2)
            eval_after = lines[0].eval if lines else Eval(cp=0)
        position_evals.append(eval_after)

        win_before = win_percent(eval_before, mover)
        win_after = win_percent(eval_after, mover)
        second_win = win_percent(second.eval, mover) if second else None

        ctx = MoveContext(
            board_before=before,
            move=move,
            best_move=best.move if best else None,
            win_before=win_before,
            win_after=win_after,
            second_win=second_win,
            in_book=in_book,
            best_is_mate=best_is_mate,
            mover_mated_before=mover_mated_before,
            prev_classification=prev_classification,
            prev_move=prev_move,
        )
        label = classify(ctx)
        acc = move_accuracy(win_before, win_after)
        color = "w" if mover == chess.WHITE else "b"
        counts[color][label] += 1
        accuracies[mover].append(acc)

        records.append(
            {
                "ply": i + 1,
                "san": san,
                "uci": move.uci(),
                "color": color,
                "eval_before": eval_before.to_json(),
                "eval_after": eval_after.to_json(),
                "best": _line_json(before, best, with_line=True),
                "second": _line_json(before, second, with_line=False),
                "win_before": round(win_before, 1),
                "win_after": round(win_after, 1),
                "accuracy": acc,
                "classification": label,
                "book": label == "book",
                "clock": clocks[i] if i < len(clocks) else None,
            }
        )
        prev_classification = label
        prev_move = move
        if on_progress:
            await on_progress(i + 1, total)

    white_wins = [win_percent_white(e) for e in position_evals]
    black_wins = [100.0 - w for w in white_wins]
    return Report(
        engine_name=engine.name,
        depth=engine.depth,
        time_ms=engine.time_ms,
        multipv=2,
        threads=engine.threads,
        hash_mb=engine.hash_mb,
        accuracy_white=game_accuracy(white_wins, accuracies[chess.WHITE]),
        accuracy_black=game_accuracy(black_wins, accuracies[chess.BLACK]),
        opening_eco=opening.eco if opening else None,
        opening_name=opening.name if opening else None,
        book_plies=book_plies,
        counts=counts,
        moves=records,
    )
