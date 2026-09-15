import type { Color, EvalJson } from '$lib/types/api';

const K = 0.00368208;

/** White's win expectancy 0..100 for a White-POV eval. */
export function winPercentWhite(ev: EvalJson | null | undefined): number {
  if (!ev) return 50;
  if ('mate' in ev) return ev.mate > 0 ? 100 : ev.mate < 0 ? 0 : 50;
  const cp = Math.max(-10000, Math.min(10000, ev.cp));
  return 50 + 50 * (2 / (1 + Math.exp(-K * cp)) - 1);
}

export function winPercent(ev: EvalJson | null | undefined, pov: Color): number {
  const w = winPercentWhite(ev);
  return pov === 'w' ? w : 100 - w;
}

/** Percentage of the eval bar that should be white, oriented to White. */
export function evalToBarPercent(ev: EvalJson | null | undefined): number {
  return winPercentWhite(ev);
}

/** "+0.35", "-1.20", "M3", "-M2". `pov` flips the sign for the given side. */
export function formatEval(ev: EvalJson | null | undefined, pov: Color = 'w'): string {
  if (!ev) return '0.00';
  const sign = pov === 'w' ? 1 : -1;
  if ('mate' in ev) {
    if (ev.mate === 0) return '#';
    const m = ev.mate * sign;
    return m > 0 ? `M${m}` : `-M${Math.abs(m)}`;
  }
  const pawns = (ev.cp * sign) / 100;
  const s = pawns.toFixed(2);
  return pawns > 0 ? `+${s}` : s;
}

/** Signed pawn value clamped for charting, White POV. Mates saturate. */
export function evalToPawns(ev: EvalJson | null | undefined, clamp = 8): number {
  if (!ev) return 0;
  if ('mate' in ev) return ev.mate > 0 ? clamp : ev.mate < 0 ? -clamp : 0;
  return Math.max(-clamp, Math.min(clamp, ev.cp / 100));
}

export function accuracyTone(acc: number | null | undefined): 'success' | 'warning' | 'danger' | 'neutral' {
  if (acc == null) return 'neutral';
  if (acc >= 85) return 'success';
  if (acc >= 70) return 'warning';
  return 'danger';
}
