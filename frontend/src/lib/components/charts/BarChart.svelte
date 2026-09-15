<script lang="ts">
  /** Vertical bars for one measure across categories, direct-labelled. */
  export interface Bar {
    label: string;
    value: number | null;
    hint?: string;
  }
  let { bars, format = (v: number) => v.toFixed(2), height = 150 }: { bars: Bar[]; format?: (v: number) => string; height?: number } = $props();

  const max = $derived(Math.max(0.01, ...bars.map((b) => b.value ?? 0)));
  let hover = $state<number | null>(null);
</script>

<div class="bars" style="height:{height}px">
  {#each bars as b, i (b.label)}
    <div class="col" role="img" aria-label="{b.label}: {b.value == null ? 'no data' : format(b.value)}" onpointerenter={() => (hover = i)} onpointerleave={() => (hover = null)} title={b.hint ?? ''}>
      <span class="val mono" class:muted={b.value == null}>{b.value == null ? '—' : format(b.value)}</span>
      <div class="track">
        <div class="fill" class:hot={hover === i} style="height:{b.value == null ? 0 : (100 * b.value) / max}%"></div>
      </div>
      <span class="lab">{b.label}</span>
    </div>
  {/each}
</div>

<style>
  .bars { display: flex; gap: 10px; align-items: stretch; }
  .col { flex: 1; display: grid; grid-template-rows: auto 1fr auto; gap: 4px; text-align: center; min-width: 0; }
  .val { font-size: var(--fs-xs); font-weight: 600; }
  .track { display: flex; align-items: flex-end; background: var(--raised); border-radius: 4px; overflow: hidden; }
  .fill { width: 100%; background: var(--info); border-radius: 4px 4px 0 0; transition: filter 120ms; min-height: 2px; }
  .fill.hot { filter: brightness(1.15); }
  .lab { font-size: var(--fs-xs); color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
