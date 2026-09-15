import { describe, expect, it } from 'vitest';
import { replayPositions, turnAt } from './replay';

describe('replayPositions', () => {
  it('produces n+1 fens and move metadata', () => {
    const r = replayPositions('1. e4 e5 2. Nf3 Nc6 *');
    expect(r.fens).toHaveLength(5);
    expect(r.moves.map((m) => m.san)).toEqual(['e4', 'e5', 'Nf3', 'Nc6']);
    expect(r.moves[0]).toMatchObject({ from: 'e2', to: 'e4', uci: 'e2e4', color: 'w', piece: 'p' });
    expect(turnAt(r.fens[1])).toBe('b');
  });
  it('handles clock comments', () => {
    const r = replayPositions('1. e4 {[%clk 0:09:57.7]} 1... e5 {[%clk 0:09:50]} *');
    expect(r.moves).toHaveLength(2);
  });
  it('flags checks and captures', () => {
    const r = replayPositions('1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7# 1-0');
    const last = r.moves.at(-1)!;
    expect(last.captured).toBe('p');
    expect(last.check).toBe(true);
  });
});
