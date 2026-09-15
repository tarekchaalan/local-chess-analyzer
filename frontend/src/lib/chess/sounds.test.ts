import { describe, expect, it, vi } from 'vitest';

vi.mock('$lib/sounds/capture.wav', () => ({ default: 'capture.wav' }));
vi.mock('$lib/sounds/castle.wav', () => ({ default: 'castle.wav' }));
vi.mock('$lib/sounds/move-check.wav', () => ({ default: 'check.wav' }));
vi.mock('$lib/sounds/move-opponent.wav', () => ({ default: 'opp.wav' }));
vi.mock('$lib/sounds/move-self.wav', () => ({ default: 'self.wav' }));
vi.mock('$lib/sounds/promote.wav', () => ({ default: 'promote.wav' }));

const { soundFor } = await import('./sounds');
const { replayPositions } = await import('./replay');

describe('soundFor', () => {
  const r = replayPositions('1. e4 d5 2. exd5 Qxd5 3. Nc3 Qe5+ 4. Be2 Nf6 5. Nf3 Qe6 6. O-O *');
  const by = (san: string) => r.moves.find((m) => m.san === san)!;

  it('distinguishes own and opponent quiet moves', () => {
    expect(soundFor(by('e4'), true)).toBe('move-self');
    expect(soundFor(by('e4'), false)).toBe('move-opponent');
  });
  it('captures, castles and checks take priority', () => {
    expect(soundFor(by('exd5'), true)).toBe('capture');
    expect(soundFor(by('O-O'), true)).toBe('castle');
    expect(soundFor(by('Qe5+'), false)).toBe('move-check');
  });
  it('promotions and mates', () => {
    const p = replayPositions('1. e4 d5 2. exd5 c6 3. dxc6 Nf6 4. cxb7 Nc6 5. bxa8=Q *');
    expect(soundFor(p.moves.at(-1)!, true)).toBe('promote');
    const m = replayPositions('1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7# 1-0');
    expect(soundFor(m.moves.at(-1)!, true)).toBe('move-check');
  });
});
