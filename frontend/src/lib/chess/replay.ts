import { Chess } from 'chess.js';
import type { Color } from '$lib/types/api';

export interface ReplayMove {
  san: string;
  uci: string;
  from: string;
  to: string;
  color: Color;
  piece: string;
  captured?: string;
  check: boolean;
}

export interface Replay {
  /** fens[0] is the start position; fens[i] is after ply i. */
  fens: string[];
  moves: ReplayMove[];
}

export function replayPositions(pgn: string): Replay {
  const chess = new Chess();
  chess.loadPgn(pgn);
  const history = chess.history({ verbose: true });
  const board = new Chess();
  const fens = [board.fen()];
  const moves: ReplayMove[] = [];
  for (const h of history) {
    board.move(h.san);
    fens.push(board.fen());
    moves.push({
      san: h.san,
      uci: h.from + h.to + (h.promotion ?? ''),
      from: h.from,
      to: h.to,
      color: h.color as Color,
      piece: h.piece,
      captured: h.captured,
      check: board.isCheck(),
    });
  }
  return { fens, moves };
}

export function turnAt(fen: string): Color {
  return fen.split(' ')[1] === 'b' ? 'b' : 'w';
}
