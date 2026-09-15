<script lang="ts">
  /** Single-series line chart with crosshair tooltip. Values are 0..100 unless `domain` is given. */
  export interface Point {
    label: string;
    value: number;
    meta?: string;
  }

  let {
    points,
    domain = [0, 100],
    unit = '%',
    height = 180,
  }: { points: Point[]; domain?: [number, number]; unit?: string; height?: number } = $props();

  const W = 640;
  const H = $derived(height);
  const PAD = { l: 34, r: 12, t: 12, b: 24 };
  const n = $derived(points.length);
  const [lo, hi] = $derived.by(() => {
    if (domain) return domain;
    const vs = points.map((p) => p.value);
    return [Math.min(...vs), Math.max(...vs)] as [number, number];
  });
  const x = (i: number) => PAD.l + (n <= 1 ? (W - PAD.l - PAD.r) / 2 : (i * (W - PAD.l - PAD.r)) / (n - 1));
  const y = (v: number) => PAD.t + ((hi - v) * (H - PAD.t - PAD.b)) / Math.max(1e-9, hi - lo);
  const path = $derived(points.map((p, i) => `${i === 0 ? 'M' : 'L'}${x(i).toFixed(1)},${y(p.value).toFixed(1)}`).join(' '));
  const ticks = $derived([lo, (lo + hi) / 2, hi]);
  const labelEvery = $derived(Math.max(1, Math.ceil(n / 8)));

  let hover = $state<number | null>(null);
  let svgEl = $state<SVGSVGElement>();
  function idxFromEvent(e: PointerEvent): number {
    const rect = svgEl!.getBoundingClientRect();
    const px = ((e.clientX - rect.left) / rect.width) * W;
    const i = Math.round(((px - PAD.l) / (W - PAD.l - PAD.r)) * (n - 1));
    return Math.max(0, Math.min(n - 1, i));
  }
</script>

<div class="chart">
  {#if n === 0}
    <p class="muted empty">No analysed games yet.</p>
  {:else}
    <svg bind:this={svgEl} viewBox="0 0 {W} {H}" preserveAspectRatio="none" style="height:{H}px" role="img" aria-label="Line chart"
      onpointermove={(e) => (hover = idxFromEvent(e))} onpointerleave={() => (hover = null)}>
      {#each ticks as t (t)}
        <line x1={PAD.l} x2={W - PAD.r} y1={y(t)} y2={y(t)} class="grid" vector-effect="non-scaling-stroke" />
        <text x={PAD.l - 6} y={y(t) + 3} class="tick" text-anchor="end">{Math.round(t)}{unit}</text>
      {/each}
      <path d={path} class="line" vector-effect="non-scaling-stroke" />
      {#each points as p, i (p.label)}
        {#if i % labelEvery === 0 || i === n - 1}
          <text x={x(i)} y={H - 6} class="tick" text-anchor={i === 0 ? 'start' : i === n - 1 ? 'end' : 'middle'}>{p.label}</text>
        {/if}
        <circle cx={x(i)} cy={y(p.value)} r={hover === i ? 5 : 3.5} class="dot" class:hot={hover === i} />
      {/each}
      {#if hover != null}
        <line x1={x(hover)} x2={x(hover)} y1={PAD.t} y2={H - PAD.b} class="cross" vector-effect="non-scaling-stroke" />
      {/if}
    </svg>
    {#if hover != null}
      {@const p = points[hover]}
      <div class="tip" style="left:{(x(hover) / W) * 100}%" class:right={x(hover) / W > 0.7}>
        <strong class="mono">{p.value.toFixed(1)}{unit}</strong>
        <span>{p.label}</span>
        {#if p.meta}<span class="muted">{p.meta}</span>{/if}
      </div>
    {/if}
  {/if}
</div>

<style>
  .chart { position: relative; width: 100%; }
  svg { width: 100%; display: block; cursor: crosshair; touch-action: none; }
  .grid { stroke: var(--border); stroke-width: 1; }
  .tick { fill: var(--text-faint); font-size: 10px; font-family: var(--mono); }
  .line { fill: none; stroke: var(--accent); stroke-width: 2; stroke-linejoin: round; stroke-linecap: round; }
  .dot { fill: var(--accent); stroke: var(--surface); stroke-width: 2; }
  .dot.hot { stroke-width: 2.5; }
  .cross { stroke: var(--text-faint); stroke-width: 1; stroke-dasharray: 3 3; }
  .tip {
    position: absolute; top: 4px; transform: translateX(10px);
    display: flex; gap: 8px; align-items: baseline;
    padding: 4px 8px; border-radius: var(--radius);
    background: var(--overlay); border: 1px solid var(--border-strong); box-shadow: var(--shadow);
    font-size: var(--fs-xs); white-space: nowrap; pointer-events: none;
  }
  .tip.right { transform: translateX(calc(-100% - 10px)); }
  .empty { padding: var(--sp-4) 0; text-align: center; font-size: var(--fs-sm); }
</style>
