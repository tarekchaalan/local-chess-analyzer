<script lang="ts">
  import { CLASSIFICATIONS, sentence } from '$lib/chess/classification';
  import { formatEval } from '$lib/chess/eval';
  import { formatClock } from '$lib/chess/clocks';
  import ClassificationIcon from '$lib/icons/classification/ClassificationIcon.svelte';
  import type { MoveRecord } from '$lib/types/api';

  let { record }: { record: MoveRecord | null } = $props();

  const moveNo = $derived(record ? `${Math.ceil(record.ply / 2)}${record.color === 'w' ? '.' : '...'}` : '');
  const showBest = $derived(record?.best && record.best.uci !== record.uci && record.classification !== 'book' && record.classification !== 'forced');
</script>

<div class="detail">
  {#if !record}
    <p class="muted">Starting position. Step through the moves or click one in the list.</p>
  {:else}
    <div class="head" style="--c:{CLASSIFICATIONS[record.classification].color}">
      <ClassificationIcon label={record.classification} size={26} />
      <div>
        <div class="title">{moveNo} {sentence(record.san, record.classification)}</div>
        <div class="muted small">{CLASSIFICATIONS[record.classification].description}</div>
      </div>
      <div class="eval mono">{formatEval(record.eval_after)}</div>
    </div>
    {#if showBest && record.best}
      <div class="best">
        <span class="muted small">Best was</span>
        <span class="san">{record.best.san}</span>
        <span class="mono muted small">{formatEval(record.best.eval)}</span>
        {#if record.best.line && record.best.line.length > 1}
          <span class="line mono muted">{record.best.line.slice(1).join(' ')}</span>
        {/if}
      </div>
    {:else if record.best?.line && record.best.line.length > 1 && record.classification !== 'book'}
      <div class="best">
        <span class="muted small">Engine line</span>
        <span class="line mono muted">{record.best.line.join(' ')}</span>
      </div>
    {/if}
    <div class="facts muted small">
      <span>win chance {record.win_before.toFixed(0)}% → {record.win_after.toFixed(0)}%</span>
      <span>move accuracy {record.accuracy.toFixed(0)}%</span>
      {#if record.clock}<span>clock {formatClock(record.clock)}</span>{/if}
    </div>
  {/if}
</div>

<style>
  .detail { display: grid; gap: var(--sp-3); }
  .head { display: grid; grid-template-columns: auto 1fr auto; gap: 10px; align-items: center; }
  .title { font-weight: 600; }
  .small { font-size: var(--fs-xs); }
  .eval { font-weight: 700; font-size: var(--fs-lg); }
  .best { display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px; padding: 8px 10px; border-radius: var(--radius); background: var(--raised); }
  .san { font-weight: 700; }
  .line { font-size: var(--fs-xs); }
  .facts { display: flex; gap: var(--sp-3); flex-wrap: wrap; }
</style>
