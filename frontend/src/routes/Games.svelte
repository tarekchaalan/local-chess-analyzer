<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api/client';
  import { accounts } from '$lib/stores/accounts.svelte';
  import { jobs } from '$lib/stores/jobs.svelte';
  import { toasts } from '$lib/stores/toasts.svelte';
  import { errorMessage, pluralize } from '$lib/format';
  import FilterBar, { type FilterState } from '$lib/components/FilterBar.svelte';
  import GameRow from '$lib/components/GameRow.svelte';
  import Pagination from '$lib/components/Pagination.svelte';
  import Button from '$lib/ui/Button.svelte';
  import EmptyState from '$lib/ui/EmptyState.svelte';
  import Icon from '$lib/ui/Icon.svelte';
  import Skeleton from '$lib/ui/Skeleton.svelte';
  import type { GameFilters, GameList, GameListItem } from '$lib/types/api';

  type SortKey = 'played_at' | 'accuracy' | 'rating';

  let filters = $state<FilterState>({ account_id: '', time_class: '', user_result: '', color: '', analysis_status: '', search: '', date_from: '', date_to: '' });
  let sort = $state<SortKey>('played_at');
  let order = $state<'asc' | 'desc'>('desc');
  let page = $state(1);
  const pageSize = 25;

  let data = $state<GameList | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let selected = $state<Set<number>>(new Set());
  let lastToggled: number | null = null;
  let analyzing = $state(false);
  let requestId = 0;

  function query(): GameFilters {
    return {
      account_id: filters.account_id ? Number(filters.account_id) : undefined,
      time_class: (filters.time_class || undefined) as GameFilters['time_class'],
      user_result: (filters.user_result || undefined) as GameFilters['user_result'],
      color: (filters.color || undefined) as GameFilters['color'],
      analysis_status: (filters.analysis_status || undefined) as GameFilters['analysis_status'],
      search: filters.search || undefined,
      date_from: filters.date_from || undefined,
      date_to: filters.date_to || undefined,
      sort,
      order,
      page,
      page_size: pageSize,
    };
  }

  async function load() {
    const id = ++requestId;
    loading = true;
    error = null;
    try {
      const res = await api.games(query());
      if (id !== requestId) return;
      data = res;
    } catch (e) {
      if (id !== requestId) return;
      error = errorMessage(e);
    } finally {
      if (id === requestId) loading = false;
    }
  }

  function filtersChanged() {
    page = 1;
    selected = new Set();
    load();
  }

  function setSort(key: SortKey) {
    if (sort === key) order = order === 'desc' ? 'asc' : 'desc';
    else {
      sort = key;
      order = 'desc';
    }
    page = 1;
    load();
  }

  function toggle(id: number, shift: boolean) {
    const next = new Set(selected);
    const items = data?.items ?? [];
    if (shift && lastToggled != null) {
      const a = items.findIndex((g) => g.id === lastToggled);
      const b = items.findIndex((g) => g.id === id);
      if (a >= 0 && b >= 0) {
        const [lo, hi] = a < b ? [a, b] : [b, a];
        for (let i = lo; i <= hi; i++) next.add(items[i].id);
      }
    } else if (next.has(id)) next.delete(id);
    else next.add(id);
    lastToggled = id;
    selected = next;
  }

  function toggleAll() {
    const items = data?.items ?? [];
    if (items.every((g) => selected.has(g.id))) selected = new Set();
    else selected = new Set(items.map((g) => g.id));
  }

  async function analyzeSelected() {
    const ids = [...selected];
    if (ids.length === 0) return;
    analyzing = true;
    try {
      const res = await api.bulkAnalyze(ids);
      res.jobs.forEach((j) => jobs.applyEvent(j));
      const msg = `Queued ${pluralize(res.jobs.length, 'game')} for analysis`;
      toasts.success(res.skipped.length ? `${msg} (${res.skipped.length} already analysed)` : msg);
      selected = new Set();
    } catch (e) {
      toasts.error(errorMessage(e));
    } finally {
      analyzing = false;
    }
  }

  // Refresh a row's status when its analysis finishes.
  $effect(() => {
    const finished = jobs.list.filter((j) => j.kind === 'analyze' && j.status === 'done');
    const ids = new Set(finished.map((j) => j.game_id));
    if (data?.items.some((g: GameListItem) => ids.has(g.id) && g.analysis_status !== 'done')) load();
  });

  function onKey(e: KeyboardEvent) {
    if (e.key === '/' && !(e.target instanceof HTMLInputElement) && !(e.target instanceof HTMLTextAreaElement)) {
      e.preventDefault();
      document.querySelector<HTMLInputElement>('#games-search')?.focus();
    }
  }

  onMount(() => {
    load();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });

  const allChecked = $derived(!!data?.items.length && data.items.every((g) => selected.has(g.id)));
</script>

<div class="page">
  <header class="head">
    <div>
      <h1>Games</h1>
      {#if data}<p class="muted">{pluralize(data.total, 'game')}</p>{/if}
    </div>
    {#if selected.size > 0}
      <div class="bulk">
        <span class="muted">{selected.size} selected</span>
        <Button variant="primary" size="sm" onclick={analyzeSelected} loading={analyzing}><Icon name="play" size={14} />Analyze</Button>
        <Button variant="ghost" size="sm" onclick={() => (selected = new Set())}>Clear</Button>
      </div>
    {/if}
  </header>

  {#if accounts.list.length === 0}
    <EmptyState icon="accounts" title="No accounts linked" description="Link a Chess.com or Lichess account to import games.">
      <Button variant="primary" href="#/accounts">Go to accounts</Button>
    </EmptyState>
  {:else}
    <FilterBar bind:filters onchange={filtersChanged} />

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th class="check"><input type="checkbox" checked={allChecked} onclick={toggleAll} aria-label="Select all on page" /></th>
            <th>Opponent</th>
            <th>Result</th>
            <th>Speed</th>
            <th><button class="sort" class:active={sort === 'played_at'} onclick={() => setSort('played_at')}>Date {#if sort === 'played_at'}{order === 'desc' ? '↓' : '↑'}{/if}</button></th>
            <th><button class="sort" class:active={sort === 'accuracy'} onclick={() => setSort('accuracy')}>Accuracy {#if sort === 'accuracy'}{order === 'desc' ? '↓' : '↑'}{/if}</button></th>
            <th>Analysis</th>
            <th class="plat"></th>
          </tr>
        </thead>
        <tbody>
          {#if loading && !data}
            {#each Array(8) as _, i (i)}
              <tr><td colspan="8"><Skeleton height="22px" /></td></tr>
            {/each}
          {:else if error}
            <tr><td colspan="8"><EmptyState icon="warning" title="Could not load games" description={error}><Button onclick={load}>Retry</Button></EmptyState></td></tr>
          {:else if data && data.items.length === 0}
            <tr><td colspan="8"><EmptyState icon="games" title="No games match" description="Try clearing a filter, or sync an account to import games." /></td></tr>
          {:else if data}
            {#each data.items as game (game.id)}
              <GameRow {game} selected={selected.has(game.id)} ontoggle={toggle} />
            {/each}
          {/if}
        </tbody>
      </table>
    </div>

    {#if data}
      <Pagination {page} {pageSize} total={data.total} onchange={(p) => { page = p; load(); }} />
    {/if}
  {/if}
</div>

<style>
  .page { display: grid; gap: var(--sp-4); }
  .head { display: flex; justify-content: space-between; align-items: flex-end; gap: var(--sp-3); flex-wrap: wrap; }
  .bulk { display: flex; align-items: center; gap: var(--sp-2); font-size: var(--fs-sm); }
  .table-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    overflow-x: auto;
  }
  table { width: 100%; border-collapse: collapse; min-width: 720px; }
  th {
    text-align: left;
    padding: 10px 12px;
    font-size: var(--fs-xs);
    color: var(--text-muted);
    font-weight: 500;
    white-space: nowrap;
  }
  th.check { width: 36px; padding-right: 0; }
  th input[type='checkbox'] { accent-color: var(--accent); width: 15px; height: 15px; cursor: pointer; }
  .sort { color: inherit; font: inherit; }
  .sort:hover, .sort.active { color: var(--text); }
  .plat { text-align: right; }
  @media (max-width: 900px) { .plat { display: none; } }
</style>
