<script lang="ts">
  import { formatDate, TIME_CLASS_LABEL } from '$lib/format';
  import type { GameListItem } from '$lib/types/api';

  let { games }: { games: GameListItem[] } = $props();
  const resultLabel = { win: 'W', loss: 'L', draw: 'D' } as const;
</script>

<ul class="recent">
  {#each games as g (g.id)}
    <li>
      <a href="#/games/{g.id}">
        <span class="res {g.user_result}">{resultLabel[g.user_result]}</span>
        <span class="dot {g.user_color}"></span>
        <span class="opp">{g.opponent}</span>
        <span class="muted small">{TIME_CLASS_LABEL[g.time_class]}</span>
        <span class="muted small date">{formatDate(g.played_at, { month: 'short', day: 'numeric' })}</span>
        <span class="mono small acc">{g.accuracy != null ? `${g.accuracy.toFixed(0)}%` : ''}</span>
      </a>
    </li>
  {/each}
</ul>

<style>
  .recent { list-style: none; margin: 0; padding: 0; display: grid; }
  li + li { border-top: 1px solid var(--border); }
  a { display: grid; grid-template-columns: 22px 10px 1fr auto auto 40px; gap: 10px; align-items: center; padding: 8px 0; text-decoration: none; }
  a:hover .opp { text-decoration: underline; }
  .res { font-size: 11px; font-weight: 700; text-align: center; border-radius: 4px; padding: 1px 0; }
  .res.win { color: var(--win); background: var(--accent-soft); }
  .res.loss { color: var(--loss); background: var(--danger-soft); }
  .res.draw { color: var(--draw); background: var(--raised); }
  .dot { width: 10px; height: 10px; border-radius: 50%; border: 1px solid var(--border-strong); }
  .dot.w { background: #f3f3f0; }
  .dot.b { background: #1b1d21; }
  .opp { font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .small { font-size: var(--fs-xs); }
  .acc { text-align: right; }
</style>
