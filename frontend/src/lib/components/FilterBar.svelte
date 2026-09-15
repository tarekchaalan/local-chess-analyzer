<script lang="ts">
  import { accounts } from '$lib/stores/accounts.svelte';
  import Input from '$lib/ui/Input.svelte';
  import Select from '$lib/ui/Select.svelte';
  import Button from '$lib/ui/Button.svelte';
  import { PLATFORM_LABEL } from '$lib/format';

  export interface FilterState {
    account_id: string;
    time_class: string;
    user_result: string;
    color: string;
    analysis_status: string;
    search: string;
    date_from: string;
    date_to: string;
  }

  let { filters = $bindable(), onchange }: { filters: FilterState; onchange: () => void } = $props();

  let searchEl = $state<HTMLInputElement | null>(null);
  let debounce: ReturnType<typeof setTimeout> | null = null;

  const accountOptions = $derived([
    { value: '', label: 'All accounts' },
    ...accounts.list.map((a) => ({ value: String(a.id), label: `${a.username} · ${PLATFORM_LABEL[a.platform]}` })),
  ]);

  function searchChanged() {
    if (debounce) clearTimeout(debounce);
    debounce = setTimeout(onchange, 250);
  }

  const dirty = $derived(
    Object.entries(filters).some(([k, v]) => v !== '' && k !== 'search') || filters.search !== '',
  );

  function clear() {
    filters = { account_id: '', time_class: '', user_result: '', color: '', analysis_status: '', search: '', date_from: '', date_to: '' };
    onchange();
  }

  export function focusSearch() {
    document.querySelector<HTMLInputElement>('#games-search')?.focus();
  }
</script>

<div class="bar">
  <div class="search">
    <Input id="games-search" type="search" placeholder="Opponent or opening  (press /)" bind:value={filters.search} oninput={searchChanged} />
  </div>
  <Select bind:value={filters.account_id} options={accountOptions} onchange={onchange} />
  <Select
    bind:value={filters.time_class}
    options={[
      { value: '', label: 'Any speed' },
      { value: 'bullet', label: 'Bullet' },
      { value: 'blitz', label: 'Blitz' },
      { value: 'rapid', label: 'Rapid' },
      { value: 'classical', label: 'Classical' },
      { value: 'daily', label: 'Daily' },
    ]}
    onchange={onchange}
  />
  <Select
    bind:value={filters.user_result}
    options={[
      { value: '', label: 'Any result' },
      { value: 'win', label: 'Wins' },
      { value: 'loss', label: 'Losses' },
      { value: 'draw', label: 'Draws' },
    ]}
    onchange={onchange}
  />
  <Select
    bind:value={filters.color}
    options={[
      { value: '', label: 'Both colours' },
      { value: 'w', label: 'As White' },
      { value: 'b', label: 'As Black' },
    ]}
    onchange={onchange}
  />
  <Select
    bind:value={filters.analysis_status}
    options={[
      { value: '', label: 'Any status' },
      { value: 'done', label: 'Analysed' },
      { value: 'none', label: 'Not analysed' },
      { value: 'queued', label: 'Queued' },
      { value: 'failed', label: 'Failed' },
    ]}
    onchange={onchange}
  />
  <Input type="date" bind:value={filters.date_from} oninput={onchange} />
  <Input type="date" bind:value={filters.date_to} oninput={onchange} />
  {#if dirty}
    <Button variant="ghost" size="sm" onclick={clear}>Clear</Button>
  {/if}
</div>

<style>
  .bar {
    display: flex;
    flex-wrap: wrap;
    gap: var(--sp-2);
    align-items: center;
  }
  .search { flex: 1 1 240px; min-width: 200px; }
  .bar :global(.field) { flex: 0 0 auto; }
</style>
