<script lang="ts">
  import { formatClock } from '$lib/chess/clocks';
  import type { Color } from '$lib/types/api';

  let {
    name,
    rating,
    color,
    clock = null,
    active = false,
    isUser = false,
    accuracy = null,
  }: {
    name: string;
    rating: number | null;
    color: Color;
    clock?: string | null;
    active?: boolean;
    isUser?: boolean;
    accuracy?: number | null;
  } = $props();
</script>

<div class="row" class:active>
  <span class="piece {color}"></span>
  <span class="name">{name}{#if isUser}<span class="you">you</span>{/if}</span>
  {#if rating}<span class="rating mono muted">{rating}</span>{/if}
  {#if accuracy != null}<span class="acc mono">{accuracy.toFixed(1)}%</span>{/if}
  <span class="spacer"></span>
  {#if clock}<span class="clock mono" class:live={active}>{formatClock(clock)}</span>{/if}
</div>

<style>
  .row { display: flex; align-items: center; gap: 8px; padding: 6px 2px; min-height: 34px; }
  .piece { width: 14px; height: 14px; border-radius: 3px; border: 1px solid var(--border-strong); flex: none; }
  .piece.w { background: #f3f3f0; }
  .piece.b { background: #1b1d21; }
  .name { font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .you { margin-left: 6px; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; color: var(--accent); }
  .rating { font-size: var(--fs-xs); }
  .acc { font-size: var(--fs-xs); color: var(--text-muted); padding: 0 6px; border-radius: 4px; background: var(--raised); }
  .spacer { flex: 1; }
  .clock {
    font-size: var(--fs-sm);
    padding: 2px 8px;
    border-radius: 4px;
    background: var(--raised);
    color: var(--text-muted);
    font-variant-numeric: tabular-nums;
  }
  .clock.live { background: var(--text); color: var(--bg); }
</style>
