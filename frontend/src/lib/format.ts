import type { Platform, TimeClass } from '$lib/types/api';

export const PLATFORM_LABEL: Record<Platform, string> = { chesscom: 'Chess.com', lichess: 'Lichess' };
export const TIME_CLASS_LABEL: Record<TimeClass, string> = {
  bullet: 'Bullet',
  blitz: 'Blitz',
  rapid: 'Rapid',
  classical: 'Classical',
  daily: 'Daily',
};

export function formatDate(iso: string | null | undefined, opts: Intl.DateTimeFormatOptions = {}): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric', ...opts });
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

export function timeAgo(iso: string | null | undefined): string {
  if (!iso) return 'never';
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return iso;
  const s = Math.max(0, Math.round((Date.now() - then) / 1000));
  if (s < 60) return 'just now';
  const m = Math.round(s / 60);
  if (m < 60) return `${m} min ago`;
  const h = Math.round(m / 60);
  if (h < 24) return `${h} hour${h === 1 ? '' : 's'} ago`;
  const d = Math.round(h / 24);
  if (d < 30) return `${d} day${d === 1 ? '' : 's'} ago`;
  return formatDate(iso);
}

export function formatNumber(n: number | null | undefined, digits = 0): string {
  if (n == null) return '—';
  return n.toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits });
}

export function formatPercent(n: number | null | undefined, digits = 1): string {
  if (n == null) return '—';
  return `${n.toFixed(digits)}%`;
}

export function pluralize(n: number, one: string, many = `${one}s`): string {
  return `${n.toLocaleString()} ${n === 1 ? one : many}`;
}

export function errorMessage(e: unknown): string {
  if (e instanceof Error) return e.message;
  return String(e);
}

/** "180" -> "3+0", "180+2" -> "3+2", "1/86400" -> "1 day", "3d" -> "3 days", "600" -> "10+0". */
export function formatTimeControl(tc: string | null | undefined): string {
  if (!tc) return '';
  const daily = /^1\/(\d+)$/.exec(tc);
  if (daily) {
    const days = Math.round(Number(daily[1]) / 86400);
    return `${days} day${days === 1 ? '' : 's'}`;
  }
  const d = /^(\d+)d$/.exec(tc);
  if (d) return `${d[1]} day${d[1] === '1' ? '' : 's'}`;
  const m = /^(\d+)(?:\+(\d+))?$/.exec(tc);
  if (!m) return tc;
  const base = Number(m[1]);
  const inc = m[2] ?? '0';
  const mins = base % 60 === 0 ? String(base / 60) : (base / 60).toFixed(1).replace(/\.0$/, '');
  return `${mins}+${inc}`;
}
