<script lang="ts">
  import { winPercentWhite, formatEval } from '$lib/chess/eval';
  import { CLASSIFICATIONS, NOTABLE } from '$lib/chess/classification';
  import type { MoveRecord } from '$lib/types/api';

  let { moves, ply, onseek }: { moves: MoveRecord[]; ply: number; onseek: (ply: number) => void } = $props();

  const W = 600;
  const H = 120;
  const PAD = { l: 4, r: 4, t: 6, b: 6 };

  // Series: white win% at each position; index 0 = start.
  const series = $derived.by(() => {
    if (moves.length === 0) return [50];
    return [winPercentWhite(moves[0].eval_before), ...moves.map((m) => winPercentWhite(m.eval_after))];
  });
  const n = $derived(series.length);
  const x = (i: number) => PAD.l + (i * (W - PAD.l - PAD.r)) / Math.max(1, n - 1);
  const y = (v: number) => PAD.t + ((100 - v) * (H - PAD.t - PAD.b)) / 100;
  const mid = $derived(y(50));

  const linePath = $derived(series.map((v, i) => `${i === 0 ? 'M' : 'L'}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' '));
  const areaPath = $derived(`${linePath} L${x(n - 1).toFixed(1)},${H - PAD.b} L${x(0).toFixed(1)},${H - PAD.b} Z`);

  const markers = $derived(
    moves
      .map((m, i) => ({ m, i: i + 1 }))
      .filter(({ m }) => NOTABLE.includes(m.classification))
      .map(({ m, i }) => ({ ply: i, cx: x(i), cy: y(series[i]), color: CLASSIFICATIONS[m.classification].color, label: CLASSIFICATIONS[m.classification].label })),
  );

  let hover = $state<number | null>(null);
  let svgEl: SVGSVGElement;

  function plyFromEvent(e: PointerEvent): number {
    const rect = svgEl.getBoundingClientRect();
    const px = ((e.clientX - rect.left) / rect.width) * W;
    const i = Math.round(((px - PAD.l) / (W - PAD.l - PAD.r)) * (n - 1));
    return Math.max(0, Math.min(n - 1, i));
  }

  const shown = $derived(hover ?? ply);
  const tip = $derived.by(() => {
    const i = shown;
    if (i <= 0 || i > moves.length) return null;
    const m = moves[i - 1];
    return {
      i,
      text: `${Math.ceil(m.ply / 2)}${m.color === 'w' ? '.' : '...'} ${m.san}`,
      eval: formatEval(m.eval_after),
      label: CLASSIFICATIONS[m.classification].label,
      color: CLASSIFICATIONS[m.classification].color,
      left: (x(i) / W) * 100,
    };
  });
</script>

<div class="graph">
  <svg
    bind:this={svgEl}
    viewBox="0 0 {W} {H}"
    preserveAspectRatio="none"
    role="img"
    aria-label="Evaluation over the game"
    onpointermove={(e) => (hover = plyFromEvent(e))}
    onpointerleave={() => (hover = null)}
    onpointerdown={(e) => onseek(plyFromEvent(e))}
  >
    <rect x="0" y="0" width={W} height={H} class="bg" />
    <rect x="0" y="0" width={W} height={mid} class="black-side" />
    <path d={areaPath} class="area" />
    <line x1="0" x2={W} y1={mid} y2={mid} class="midline" />
    <path d={linePath} class="line" vector-effect="non-scaling-stroke" />
    <line x1={x(shown)} x2={x(shown)} y1="0" y2={H} class="cursor" vector-effect="non-scaling-stroke" />
    {#each markers as mk (mk.ply)}
      <circle cx={mk.cx} cy={mk.cy} r="5" class="ring" />
      <circle cx={mk.cx} cy={mk.cy} r="3.5" fill={mk.color}>
        <title>{mk.label}</title>
      </circle>
    {/each}
  </svg>
  {#if tip}
    <div class="tip" style="left:{tip.left}%" class:right={tip.left > 70}>
      <strong class="mono">{tip.eval}</strong>
      <span>{tip.text}</span>
      <span class="lab" style="--c:{tip.color}">{tip.label}</span>
    </div>
  {/if}
</div>

<style>
  .graph { position: relative; width: 100%; }
  svg { width: 100%; height: 110px; display: block; cursor: crosshair; border-radius: var(--radius); overflow: hidden; touch-action: none; }
  .bg { fill: #e9e9e4; }
  .black-side { fill: #2a2d33; }
  .area { fill: #e9e9e4; }
  .midline { stroke: var(--text-faint); stroke-width: 1; stroke-dasharray: 3 3; vector-effect: non-scaling-stroke; }
  .line { fill: none; stroke: #6d7480; stroke-width: 2; stroke-linejoin: round; }
  .cursor { stroke: var(--accent); stroke-width: 1.5; }
  .ring { fill: var(--surface); }
  .tip {
    position: absolute;
    top: 6px;
    transform: translateX(8px);
    display: flex;
    align-items: baseline;
    gap: 8px;
    padding: 4px 8px;
    border-radius: var(--radius);
    background: var(--overlay);
    border: 1px solid var(--border-strong);
    box-shadow: var(--shadow);
    font-size: var(--fs-xs);
    white-space: nowrap;
    pointer-events: none;
  }
  .tip.right { transform: translateX(calc(-100% - 8px)); }
  .tip strong { font-size: var(--fs-sm); }
  .lab { color: var(--c); font-weight: 600; }
</style>
