<script lang="ts">
  import ClassificationIcon from '$lib/icons/classification/ClassificationIcon.svelte';
  import type { Classification } from '$lib/types/api';

  export interface MoveCell {
    ply: number;
    san: string;
    classification?: Classification;
  }

  let { moves, ply, onseek }: { moves: MoveCell[]; ply: number; onseek: (ply: number) => void } = $props();

  let listEl: HTMLDivElement;
  const rows = $derived.by(() => {
    const out: { n: number; w: MoveCell | undefined; b: MoveCell | undefined }[] = [];
    for (let i = 0; i < moves.length; i += 2) out.push({ n: i / 2 + 1, w: moves[i], b: moves[i + 1] });
    return out;
  });

  $effect(() => {
    const active = listEl?.querySelector<HTMLElement>(`[data-ply="${ply}"]`);
    active?.scrollIntoView({ block: 'nearest' });
  });
</script>

<div class="list" bind:this={listEl}>
  {#each rows as row (row.n)}
    <div class="row">
      <span class="num mono">{row.n}.</span>
      {#each [row.w, row.b] as cell, i (i)}
        {#if cell}
          <button class="mv" class:active={cell.ply === ply} class:bad={cell.classification && ['inaccuracy', 'mistake', 'miss', 'blunder'].includes(cell.classification)} data-ply={cell.ply} onclick={() => onseek(cell.ply)}>
            <span class="san">{cell.san}</span>
            {#if cell.classification && cell.classification !== 'best' && cell.classification !== 'excellent' && cell.classification !== 'good'}
              <ClassificationIcon label={cell.classification} size={14} />
            {/if}
          </button>
        {:else}
          <span class="mv empty"></span>
        {/if}
      {/each}
    </div>
  {/each}
</div>

<style>
  .list { overflow-y: auto; font-size: var(--fs-sm); }
  .row { display: grid; grid-template-columns: 40px 1fr 1fr; align-items: stretch; }
  .row:nth-child(even) { background: var(--hover); }
  .num { color: var(--text-faint); padding: 4px 8px; font-size: var(--fs-xs); display: flex; align-items: center; }
  .mv {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 8px;
    text-align: left;
    color: var(--text);
    border-radius: 4px;
    margin: 1px;
  }
  .mv:hover { background: var(--active); }
  .mv.active { background: var(--accent-soft); color: var(--text); box-shadow: inset 0 0 0 1px var(--accent); }
  .san { font-weight: 500; }
  .mv.bad .san { color: var(--text); }
  .empty { pointer-events: none; }
</style>
