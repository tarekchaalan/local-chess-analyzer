<script lang="ts">
  import { jobs } from '$lib/stores/jobs.svelte';
  import { gameStatus } from '$lib/stores/gameStatus.svelte';
  import { formatDate, formatTimeControl, TIME_CLASS_LABEL } from '$lib/format';
  import { accuracyTone } from '$lib/chess/eval';
  import Badge from '$lib/ui/Badge.svelte';
  import Spinner from '$lib/ui/Spinner.svelte';
  import PlatformBadge from './PlatformBadge.svelte';
  import type { GameListItem } from '$lib/types/api';

  let {
    game,
    selected = false,
    ontoggle,
  }: { game: GameListItem; selected?: boolean; ontoggle?: (id: number, shift: boolean) => void } = $props();

  const job = $derived(jobs.forGame(game.id));
  const status = $derived(job ? job.status : gameStatus.of(game));
  const resultLabel = { win: 'Win', loss: 'Loss', draw: 'Draw' } as const;
</script>

<tr class:selected>
  <td class="check" onclick={(e) => e.stopPropagation()}>
    <input type="checkbox" checked={selected} onclick={(e) => ontoggle?.(game.id, (e as MouseEvent).shiftKey)} aria-label="Select game" />
  </td>
  <td>
    <a class="opp" href="#/games/{game.id}">
      <span class="dot {game.user_color}" title={game.user_color === 'w' ? 'You played White' : 'You played Black'}></span>
      <span class="name">{game.opponent}</span>
      {#if game.opponent_rating}<span class="muted mono rating">{game.opponent_rating}</span>{/if}
    </a>
    {#if game.opening_name}<span class="opening muted">{game.opening_name}</span>{/if}
  </td>
  <td><span class="result {game.user_result}">{resultLabel[game.user_result]}</span></td>
  <td class="muted nowrap">{TIME_CLASS_LABEL[game.time_class]}{#if game.time_control}&nbsp;<span class="tc mono">{formatTimeControl(game.time_control)}</span>{/if}</td>
  <td class="muted nowrap">{formatDate(game.played_at)}</td>
  <td class="mono">
    {#if game.accuracy != null}
      <span class="acc {accuracyTone(game.accuracy)}">{game.accuracy.toFixed(1)}%</span>
    {:else}
      <span class="faint">—</span>
    {/if}
  </td>
  <td>
    {#if status === 'running'}
      <Badge tone="info"><Spinner size={11} />{job && job.total ? `${Math.round((100 * job.progress) / job.total)}%` : 'Analysing'}</Badge>
    {:else if status === 'queued'}
      <Badge>Queued</Badge>
    {:else if status === 'done'}
      <Badge tone="success">Analysed</Badge>
    {:else if status === 'failed'}
      <Badge tone="danger">Failed</Badge>
    {:else}
      <span class="faint">—</span>
    {/if}
  </td>
  <td class="plat"><PlatformBadge platform={game.platform} size="sm" /></td>
</tr>

<style>
  tr { border-top: 1px solid var(--border); }
  tr:hover { background: var(--hover); }
  tr.selected { background: var(--accent-soft); }
  td { padding: 10px 12px; vertical-align: middle; font-size: var(--fs-sm); }
  .check { width: 36px; padding-right: 0; }
  input[type='checkbox'] { accent-color: var(--accent); width: 15px; height: 15px; cursor: pointer; }
  .opp { display: flex; align-items: center; gap: 8px; font-weight: 500; text-decoration: none; }
  .opp:hover .name { text-decoration: underline; }
  .dot { width: 10px; height: 10px; border-radius: 50%; border: 1px solid var(--border-strong); flex: none; }
  .dot.w { background: #f3f3f0; }
  .dot.b { background: #1b1d21; }
  .rating { font-size: var(--fs-xs); }
  .opening { display: block; font-size: var(--fs-xs); margin-top: 2px; padding-left: 18px; max-width: 34ch; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .result { font-weight: 600; font-size: var(--fs-xs); padding: 1px 8px; border-radius: 999px; }
  .result.win { color: var(--win); background: var(--accent-soft); }
  .result.loss { color: var(--loss); background: var(--danger-soft); }
  .result.draw { color: var(--draw); background: var(--raised); }
  .tc { font-size: var(--fs-xs); }
  .nowrap { white-space: nowrap; }
  .acc.success { color: var(--accent); }
  .acc.warning { color: var(--warning); }
  .acc.danger { color: var(--danger); }
  .plat { text-align: right; }
  @media (max-width: 900px) {
    .plat, .tc { display: none; }
  }
</style>
