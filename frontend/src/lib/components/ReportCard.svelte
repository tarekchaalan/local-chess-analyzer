<script lang="ts">
  import { CLASSIFICATIONS, REPORT_ORDER } from '$lib/chess/classification';
  import ClassificationIcon from '$lib/icons/classification/ClassificationIcon.svelte';
  import type { Analysis, Game } from '$lib/types/api';

  let { analysis, game }: { analysis: Analysis; game: Game } = $props();

  const rows = $derived(REPORT_ORDER.filter((c) => (analysis.counts.w[c] ?? 0) + (analysis.counts.b[c] ?? 0) > 0 || ['best', 'inaccuracy', 'mistake', 'blunder'].includes(c)));
</script>

<div class="report">
  <div class="acc-grid">
    <div class="acc-head"></div>
    <div class="acc-head name">{game.white}</div>
    <div class="acc-head name">{game.black}</div>

    <div class="label">Accuracy</div>
    <div class="value big mono">{analysis.accuracy_white.toFixed(1)}</div>
    <div class="value big mono">{analysis.accuracy_black.toFixed(1)}</div>

    {#if game.platform_accuracy_white != null || game.platform_accuracy_black != null}
      <div class="label muted small">Chess.com's figure</div>
      <div class="value mono muted small">{game.platform_accuracy_white?.toFixed(1) ?? '—'}</div>
      <div class="value mono muted small">{game.platform_accuracy_black?.toFixed(1) ?? '—'}</div>
    {/if}
  </div>

  <div class="counts">
    {#each rows as c (c)}
      <div class="crow">
        <span class="cname"><ClassificationIcon label={c} size={18} /> {CLASSIFICATIONS[c].label}</span>
        <span class="count mono" class:zero={!analysis.counts.w[c]}>{analysis.counts.w[c] ?? 0}</span>
        <span class="count mono" class:zero={!analysis.counts.b[c]}>{analysis.counts.b[c] ?? 0}</span>
      </div>
    {/each}
  </div>

  <div class="meta muted small">
    {analysis.engine_name} · depth {analysis.depth}{#if analysis.time_ms}, ≤{(analysis.time_ms / 1000).toFixed(1)}s/move{/if}
    {#if analysis.opening_name} · {analysis.opening_eco} {analysis.opening_name}{/if}
  </div>
</div>

<style>
  .report { display: grid; gap: var(--sp-3); }
  .acc-grid { display: grid; grid-template-columns: 1fr 72px 72px; align-items: center; row-gap: 2px; }
  .acc-head { font-size: var(--fs-xs); color: var(--text-muted); text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; padding-bottom: 4px; }
  .label { font-size: var(--fs-sm); }
  .value { text-align: center; }
  .big { font-size: var(--fs-xl); font-weight: 700; }
  .small { font-size: var(--fs-xs); }
  .counts { display: grid; gap: 2px; border-top: 1px solid var(--border); padding-top: var(--sp-2); }
  .crow { display: grid; grid-template-columns: 1fr 72px 72px; align-items: center; padding: 3px 0; }
  .cname { display: inline-flex; align-items: center; gap: 8px; font-size: var(--fs-sm); }
  .count { text-align: center; font-weight: 600; }
  .count.zero { color: var(--text-faint); font-weight: 400; }
  .meta { border-top: 1px solid var(--border); padding-top: var(--sp-2); }
</style>
