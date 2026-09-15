<script lang="ts">
  import { evalToBarPercent, formatEval } from '$lib/chess/eval';
  import type { EvalJson as E } from '$lib/types/api';

  function barLabel(ev: E | null): string {
    if (!ev) return '0.0';
    if ('mate' in ev) return ev.mate === 0 ? '#' : `M${Math.abs(ev.mate)}`;
    return Math.abs(ev.cp / 100).toFixed(1);
  }
  import type { Color, EvalJson } from '$lib/types/api';

  let { value, orientation = 'w' }: { value: EvalJson | null; orientation?: Color } = $props();

  const white = $derived(evalToBarPercent(value));
  // Unsigned: the bar itself shows who is ahead.
  const label = $derived(barLabel(value));
  const whiteOnTop = $derived(orientation === 'b');
  const whiteLeads = $derived(white >= 50);
</script>

<div class="bar" class:flip={whiteOnTop} role="img" aria-label="Evaluation {formatEval(value)}">
  <div class="white" style="height:{white}%"></div>
  <span class="label mono" class:top={whiteLeads !== whiteOnTop} class:onwhite={whiteLeads}>{label}</span>
</div>

<style>
  .bar {
    position: relative;
    width: 22px;
    height: 100%;
    background: #1f2226;
    border-radius: 4px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    border: 1px solid var(--border-strong);
  }
  .bar.flip { justify-content: flex-start; }
  .white { background: #eef0ee; width: 100%; transition: height 240ms var(--ease); }
  .label {
    position: absolute;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 9px;
    font-weight: 700;
    color: #eef0ee;
    bottom: 4px;
  }
  .label.top { top: 4px; bottom: auto; }
  .label.onwhite { color: #1f2226; }
</style>
