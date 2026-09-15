import { describe, expect, it } from 'vitest';
import { evalToBarPercent, evalToPawns, formatEval, winPercent } from './eval';

describe('formatEval', () => {
  it('formats centipawns with sign', () => {
    expect(formatEval({ cp: 35 })).toBe('+0.35');
    expect(formatEval({ cp: -120 })).toBe('-1.20');
    expect(formatEval({ cp: 0 })).toBe('0.00');
  });
  it('formats mates', () => {
    expect(formatEval({ mate: 3 })).toBe('M3');
    expect(formatEval({ mate: -2 })).toBe('-M2');
    expect(formatEval({ mate: 0 })).toBe('#');
  });
  it('flips for black pov', () => {
    expect(formatEval({ cp: 35 }, 'b')).toBe('-0.35');
    expect(formatEval({ mate: 3 }, 'b')).toBe('-M3');
  });
});

describe('win percent', () => {
  it('is 50 at equality and symmetric', () => {
    expect(evalToBarPercent({ cp: 0 })).toBeCloseTo(50);
    expect(winPercent({ cp: 100 }, 'w')).toBeCloseTo(59.1, 0);
    expect(winPercent({ cp: 100 }, 'b')).toBeCloseTo(40.9, 0);
    expect(evalToBarPercent({ mate: -1 })).toBe(0);
  });
});

describe('evalToPawns', () => {
  it('clamps', () => {
    expect(evalToPawns({ cp: 2500 })).toBe(8);
    expect(evalToPawns({ mate: -4 })).toBe(-8);
    expect(evalToPawns({ cp: -150 })).toBe(-1.5);
  });
});
