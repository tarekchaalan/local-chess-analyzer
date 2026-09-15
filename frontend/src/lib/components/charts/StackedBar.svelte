<script lang="ts">
  /** Horizontal 100% stacked bars with legend and direct labels. */
  export interface Segment {
    key: string;
    label: string;
    value: number;
    color: string;
  }
  export interface Row {
    label: string;
    segments: Segment[];
  }

  let { rows, legend }: { rows: Row[]; legend: { key: string; label: string; color: string }[] } = $props();

  let hover = $state<{ row: number; key: string } | null>(null);
  const total = (r: Row) => r.segments.reduce((s, x) => s + x.value, 0);
</script>

<div class="stack">
  <div class="legend">
    {#each legend as l (l.key)}
      <span class="lg"><i style="background:{l.color}"></i>{l.label}</span>
    {/each}
  </div>
  {#each rows as row, ri (row.label)}
    {@const t = total(row)}
    <div class="row">
      <span class="rlabel">{row.label}</span>
      <div class="bar" role="img" aria-label="{row.label}: {row.segments.map((s) => `${s.label} ${s.value}`).join(', ')}">
        {#each row.segments as s (s.key)}
          {#if s.value > 0}
            <div class="seg" role="img" aria-label="{s.label}: {s.value}" class:dim={hover && hover.row === ri && hover.key !== s.key} style="flex:{s.value};background:{s.color}"
              onpointerenter={() => (hover = { row: ri, key: s.key })} onpointerleave={() => (hover = null)}
              title="{s.label}: {s.value} ({t ? Math.round((100 * s.value) / t) : 0}%)">
              {#if t && s.value / t > 0.12}<span class="val mono">{Math.round((100 * s.value) / t)}%</span>{/if}
            </div>
          {/if}
        {/each}
        {#if t === 0}<div class="seg none">no games</div>{/if}
      </div>
      <span class="total mono muted">{t.toLocaleString()}</span>
    </div>
  {/each}
</div>

<style>
  .stack { display: grid; gap: 10px; }
  .legend { display: flex; gap: var(--sp-3); font-size: var(--fs-xs); color: var(--text-muted); }
  .lg { display: inline-flex; align-items: center; gap: 6px; }
  .lg i { width: 10px; height: 10px; border-radius: 2px; display: inline-block; }
  .row { display: grid; grid-template-columns: 64px 1fr 48px; align-items: center; gap: 10px; }
  .rlabel { font-size: var(--fs-sm); }
  .bar { display: flex; gap: 2px; height: 22px; border-radius: 4px; overflow: hidden; background: var(--raised); }
  .seg { display: flex; align-items: center; justify-content: center; min-width: 2px; transition: opacity 120ms; }
  .seg.dim { opacity: 0.45; }
  .seg.none { flex: 1; font-size: var(--fs-xs); color: var(--text-faint); }
  .val { font-size: 11px; font-weight: 600; color: #fff; mix-blend-mode: normal; }
  .total { text-align: right; font-size: var(--fs-xs); }
</style>
