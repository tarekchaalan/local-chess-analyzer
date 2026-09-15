/** "0:09:57.7" -> "9:57", "1:03:00" -> "1:03:00", "0:00:08.4" -> "0:08.4". */
export function formatClock(clock: string | null | undefined): string {
  if (!clock) return '';
  const m = /^(\d+):(\d{2}):(\d{2})(?:\.(\d))?$/.exec(clock);
  if (!m) return clock;
  const [, h, mm, ss, d] = m;
  const hours = Number(h);
  const mins = Number(mm);
  const totalSeconds = hours * 3600 + mins * 60 + Number(ss);
  if (hours > 0) return `${hours}:${mm}:${ss}`;
  if (totalSeconds < 20 && d) return `${mins}:${ss}.${d}`;
  return `${mins}:${ss}`;
}
