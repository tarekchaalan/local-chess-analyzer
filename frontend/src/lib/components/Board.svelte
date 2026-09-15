<script lang="ts">
  import { onMount } from 'svelte';
  import { Chessground } from 'chessground';
  import type { Api } from 'chessground/api';
  import type { Key } from 'chessground/types';
  import type { DrawShape } from 'chessground/draw';
  import 'chessground/assets/chessground.base.css';
  import 'chessground/assets/chessground.cburnett.css';
  import ClassificationIcon from '$lib/icons/classification/ClassificationIcon.svelte';
  import type { Classification, Color } from '$lib/types/api';

  let {
    fen,
    orientation = 'w',
    lastMove = null,
    check = false,
    bestMove = null,
    marker = null,
  }: {
    fen: string;
    orientation?: Color;
    lastMove?: [string, string] | null;
    check?: Color | false;
    bestMove?: [string, string] | null;
    marker?: { square: string; classification: Classification } | null;
  } = $props();

  let el: HTMLDivElement;
  let api: Api | null = null;
  let size = $state(0);

  onMount(() => {
    api = Chessground(el, {
      fen,
      orientation: orientation === 'w' ? 'white' : 'black',
      viewOnly: true,
      coordinates: true,
      animation: { enabled: true, duration: 180 },
      drawable: { enabled: false, visible: true },
    });
    const ro = new ResizeObserver(() => (size = el.clientWidth));
    ro.observe(el);
    size = el.clientWidth;
    return () => {
      ro.disconnect();
      api?.destroy();
      api = null;
    };
  });

  $effect(() => {
    if (!api) return;
    const shapes: DrawShape[] = bestMove
      ? [{ orig: bestMove[0] as Key, dest: bestMove[1] as Key, brush: 'paleGreen' }]
      : [];
    api.set({
      fen,
      orientation: orientation === 'w' ? 'white' : 'black',
      lastMove: lastMove ? (lastMove as [Key, Key]) : undefined,
      check: check === 'w' ? 'white' : check === 'b' ? 'black' : false,
      drawable: { enabled: false, visible: true, shapes },
    });
  });

  const markerPos = $derived.by(() => {
    if (!marker || !size) return null;
    const f = marker.square.charCodeAt(0) - 97;
    const r = Number(marker.square[1]);
    const x = orientation === 'w' ? f : 7 - f;
    const y = orientation === 'w' ? 8 - r : r - 1;
    const sq = size / 8;
    const icon = Math.max(16, Math.round(sq * 0.42));
    return { left: x * sq + sq - icon * 0.62, top: y * sq - icon * 0.38, icon };
  });
</script>

<div class="wrap">
  <div class="board" bind:this={el}></div>
  {#if marker && markerPos}
    <div class="marker" style="left:{markerPos.left}px;top:{markerPos.top}px">
      <ClassificationIcon label={marker.classification} size={markerPos.icon} />
    </div>
  {/if}
</div>

<style>
  .wrap { position: relative; width: 100%; aspect-ratio: 1; user-select: none; }
  .board { width: 100%; height: 100%; }
  .marker {
    position: absolute;
    pointer-events: none;
    filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.5));
    z-index: 3;
  }
  /* Board theme built from tokens: a 180°-symmetric checker so both orientations work. */
  .wrap :global(cg-board) {
    background: repeating-conic-gradient(var(--board-light) 0 25%, var(--board-dark) 0 50%) 0 0 / 25% 25%;
    border-radius: 4px;
  }
  .wrap :global(.cg-wrap) { border-radius: 4px; }
  .wrap :global(cg-board square.last-move) { background-color: var(--board-last-move); }
  .wrap :global(cg-board square.check) { background: var(--board-check); }
  .wrap :global(cg-board square.selected) { background-color: rgba(20, 85, 30, 0.5); }
  .wrap :global(.cg-wrap coords) { font-size: 10px; font-family: var(--mono); font-weight: 600; }
  .wrap :global(.cg-wrap coords.ranks coord),
  .wrap :global(.cg-wrap coords.files coord) { color: var(--board-dark); }
  .wrap :global(.cg-wrap coords.ranks coord:nth-child(2n)),
  .wrap :global(.cg-wrap coords.files coord:nth-child(2n)) { color: var(--board-light); }
  .wrap :global(.cg-wrap.orientation-black coords.ranks coord),
  .wrap :global(.cg-wrap.orientation-black coords.files coord) { color: var(--board-light); }
  .wrap :global(.cg-wrap.orientation-black coords.ranks coord:nth-child(2n)),
  .wrap :global(.cg-wrap.orientation-black coords.files coord:nth-child(2n)) { color: var(--board-dark); }
  .wrap :global(.cg-wrap svg.cg-shapes) { opacity: 0.85; }
</style>
