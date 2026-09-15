<script lang="ts">
  let {
    value = 0,
    max = 0,
    indeterminate = false,
    tone = 'accent',
    height = 6,
  }: { value?: number; max?: number; indeterminate?: boolean; tone?: 'accent' | 'info'; height?: number } = $props();

  const pct = $derived(max > 0 ? Math.min(100, Math.round((100 * value) / max)) : 0);
  const indet = $derived(indeterminate || max === 0);
</script>

<div class="bar {tone}" style="height:{height}px" role="progressbar" aria-valuenow={indet ? undefined : pct} aria-valuemin={0} aria-valuemax={100}>
  <div class="fill" class:indet style="width:{indet ? 40 : pct}%"></div>
</div>

<style>
  .bar { width: 100%; background: var(--raised); border-radius: 999px; overflow: hidden; }
  .fill { height: 100%; border-radius: 999px; background: var(--accent); transition: width 240ms var(--ease); }
  .info .fill { background: var(--info); }
  .indet { animation: slide 1.2s infinite ease-in-out; }
  @keyframes slide {
    from { transform: translateX(-100%); }
    to { transform: translateX(250%); }
  }
</style>
