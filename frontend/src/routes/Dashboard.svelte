<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api/client';
  import { accounts } from '$lib/stores/accounts.svelte';
  import { jobs } from '$lib/stores/jobs.svelte';
  import { errorMessage, formatPercent, PLATFORM_LABEL, TIME_CLASS_LABEL } from '$lib/format';
  import LineChart, { type Point } from '$lib/components/charts/LineChart.svelte';
  import StackedBar, { type Row } from '$lib/components/charts/StackedBar.svelte';
  import BarChart, { type Bar } from '$lib/components/charts/BarChart.svelte';
  import RecentGames from '$lib/components/RecentGames.svelte';
  import StatTile from '$lib/components/StatTile.svelte';
  import Button from '$lib/ui/Button.svelte';
  import Card from '$lib/ui/Card.svelte';
  import EmptyState from '$lib/ui/EmptyState.svelte';
  import Select from '$lib/ui/Select.svelte';
  import Skeleton from '$lib/ui/Skeleton.svelte';
  import Tabs from '$lib/ui/Tabs.svelte';
  import type { GameListItem, OpeningStat, Overview, ResultsByColor, TimeClassStat, TrendPoint } from '$lib/types/api';

  let accountId = $state('');
  let bucket = $state<'week' | 'month'>('month');
  let overview = $state<Overview | null>(null);
  let trend = $state<TrendPoint[]>([]);
  let byClass = $state<TimeClassStat[]>([]);
  let openings = $state<OpeningStat[]>([]);
  let results = $state<ResultsByColor | null>(null);
  let recent = $state<GameListItem[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);

  const acc = $derived(accountId ? Number(accountId) : undefined);

  async function load() {
    loading = true;
    error = null;
    try {
      [overview, trend, byClass, openings, results, recent] = await Promise.all([
        api.overview(acc),
        api.accuracyTrend(bucket, acc),
        api.byTimeClass(acc),
        api.openings(acc, undefined, 8),
        api.results(acc),
        api.games({ account_id: acc, page_size: 6 }).then((r) => r.items),
      ]);
    } catch (e) {
      error = errorMessage(e);
    } finally {
      loading = false;
    }
  }

  async function loadTrend() {
    try {
      trend = await api.accuracyTrend(bucket, acc);
    } catch (e) {
      error = errorMessage(e);
    }
  }

  // Refresh when analyses complete.
  let lastDone = 0;
  $effect(() => {
    const done = jobs.list.filter((j) => j.status === 'done').length;
    if (done !== lastDone) {
      lastDone = done;
      if (!loading) load();
    }
  });

  onMount(load);

  const trendPoints = $derived<Point[]>(trend.map((t) => ({ label: t.bucket, value: t.accuracy, meta: `${t.games} games` })));
  const resultRows = $derived<Row[]>(
    results
      ? (['white', 'black'] as const).map((c) => ({
          label: c === 'white' ? 'As White' : 'As Black',
          segments: [
            { key: 'win', label: 'Wins', value: results![c].wins, color: 'var(--win)' },
            { key: 'draw', label: 'Draws', value: results![c].draws, color: 'var(--draw)' },
            { key: 'loss', label: 'Losses', value: results![c].losses, color: 'var(--loss)' },
          ],
        }))
      : [],
  );
  const blunderBars = $derived<Bar[]>(byClass.map((c) => ({ label: TIME_CLASS_LABEL[c.time_class], value: c.blunders_per_game, hint: `${c.analyzed} analysed of ${c.games}` })));
  const legend = [
    { key: 'win', label: 'Wins', color: 'var(--win)' },
    { key: 'draw', label: 'Draws', color: 'var(--draw)' },
    { key: 'loss', label: 'Losses', color: 'var(--loss)' },
  ];
  const accountOptions = $derived([
    { value: '', label: 'All accounts' },
    ...accounts.list.map((a) => ({ value: String(a.id), label: `${a.username} · ${PLATFORM_LABEL[a.platform]}` })),
  ]);
</script>

<div class="dash">
  <header class="head">
    <h1>Dashboard</h1>
    {#if accounts.list.length > 1}
      <Select bind:value={accountId} options={accountOptions} onchange={load} />
    {/if}
  </header>

  {#if accounts.list.length === 0}
    <EmptyState icon="accounts" title="Link an account to get started" description="Import your games from Chess.com or Lichess and analyse them with Stockfish.">
      <Button variant="primary" href="#/accounts">Link account</Button>
    </EmptyState>
  {:else if error}
    <EmptyState icon="warning" title="Could not load stats" description={error}><Button onclick={load}>Retry</Button></EmptyState>
  {:else}
    <div class="tiles">
      {#if loading && !overview}
        {#each Array(4) as _, i (i)}<Skeleton height="86px" radius="10px" />{/each}
      {:else if overview}
        <StatTile label="Games" value={overview.games.toLocaleString()} hint={`${overview.accounts} account${overview.accounts === 1 ? '' : 's'}`} />
        <StatTile label="Analysed" value={overview.analyzed.toLocaleString()} hint={overview.games ? `${Math.round((100 * overview.analyzed) / overview.games)}% of library` : undefined} />
        <StatTile label="Mean accuracy" value={overview.mean_accuracy != null ? formatPercent(overview.mean_accuracy) : '—'} tone={overview.mean_accuracy == null ? 'neutral' : overview.mean_accuracy >= 80 ? 'success' : 'neutral'} hint="across analysed games" />
        <StatTile label="Win rate" value={overview.win_rate != null ? formatPercent(overview.win_rate) : '—'} hint={`${overview.wins}W · ${overview.draws}D · ${overview.losses}L`} />
      {/if}
    </div>

    <div class="grid">
      <Card title="Accuracy over time" subtitle="Your accuracy in analysed games" class="span2">
        {#snippet actions()}
          <Tabs bind:value={bucket} options={[{ value: 'month', label: 'Monthly' }, { value: 'week', label: 'Weekly' }]} size="sm" onchange={loadTrend} />
        {/snippet}
        <LineChart points={trendPoints} domain={[0, 100]} />
      </Card>

      <Card title="Results by colour">
        <StackedBar rows={resultRows} {legend} />
      </Card>

      <Card title="Blunders per game" subtitle="By time control, analysed games only">
        {#if byClass.length}
          <BarChart bars={blunderBars} />
        {:else}
          <p class="muted">No games yet.</p>
        {/if}
      </Card>

      <Card title="Most played openings">
        {#if openings.length === 0}
          <p class="muted">No openings recorded yet.</p>
        {:else}
          <ol class="openings">
            {#each openings as o (o.name)}
              <li>
                <span class="oname"><span class="eco mono muted">{o.eco ?? ''}</span>{o.name}</span>
                <span class="ogames mono muted">{o.games}</span>
                <span class="owr" title="{o.wins}W {o.draws}D {o.losses}L">
                  <span class="wr-bar"><span style="width:{o.win_rate ?? 0}%"></span></span>
                  <span class="mono">{o.win_rate != null ? `${Math.round(o.win_rate)}%` : '—'}</span>
                </span>
              </li>
            {/each}
          </ol>
        {/if}
      </Card>

      <Card title="Recent games">
        {#snippet actions()}<a class="more" href="#/games">All games →</a>{/snippet}
        <RecentGames games={recent} />
      </Card>
    </div>
  {/if}
</div>

<style>
  .dash { display: grid; gap: var(--sp-4); }
  .head { display: flex; justify-content: space-between; align-items: center; gap: var(--sp-3); flex-wrap: wrap; }
  .tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: var(--sp-3); }
  .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--sp-3); }
  .grid :global(.span2) { grid-column: span 2; }
  .openings { list-style: none; margin: 0; padding: 0; display: grid; gap: 6px; }
  .openings li { display: grid; grid-template-columns: 1fr 36px 110px; gap: 10px; align-items: center; font-size: var(--fs-sm); }
  .oname { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .eco { font-size: var(--fs-xs); margin-right: 6px; }
  .ogames { text-align: right; font-size: var(--fs-xs); }
  .owr { display: grid; grid-template-columns: 1fr 36px; gap: 6px; align-items: center; font-size: var(--fs-xs); }
  .wr-bar { height: 6px; background: var(--raised); border-radius: 3px; overflow: hidden; display: block; }
  .wr-bar span { display: block; height: 100%; background: var(--accent); }
  .more { font-size: var(--fs-xs); color: var(--text-muted); }
  @media (max-width: 900px) {
    .grid { grid-template-columns: 1fr; }
    .grid :global(.span2) { grid-column: auto; }
  }
</style>
