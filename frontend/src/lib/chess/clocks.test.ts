import { describe, expect, it } from 'vitest';
import { formatClock } from './clocks';

describe('formatClock', () => {
  it('drops leading hours and tenths when not low', () => {
    expect(formatClock('0:09:57.7')).toBe('9:57');
    expect(formatClock('0:00:08.4')).toBe('0:08.4');
    expect(formatClock('1:03:00')).toBe('1:03:00');
    expect(formatClock(null)).toBe('');
    expect(formatClock('weird')).toBe('weird');
  });
});
