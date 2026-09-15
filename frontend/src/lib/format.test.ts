import { describe, expect, it } from 'vitest';
import { formatTimeControl } from './format';

describe('formatTimeControl', () => {
  it('formats seconds and increments', () => {
    expect(formatTimeControl('180')).toBe('3+0');
    expect(formatTimeControl('180+2')).toBe('3+2');
    expect(formatTimeControl('600')).toBe('10+0');
    expect(formatTimeControl('90+1')).toBe('1.5+1');
    expect(formatTimeControl('1/86400')).toBe('1 day');
    expect(formatTimeControl('3d')).toBe('3 days');
    expect(formatTimeControl(null)).toBe('');
  });
});
