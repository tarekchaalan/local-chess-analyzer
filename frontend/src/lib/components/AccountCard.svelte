<script lang="ts">
  import { accounts } from '$lib/stores/accounts.svelte';
  import { jobs } from '$lib/stores/jobs.svelte';
  import { toasts } from '$lib/stores/toasts.svelte';
  import { api } from '$lib/api/client';
  import { errorMessage, pluralize, timeAgo } from '$lib/format';
  import Button from '$lib/ui/Button.svelte';
  import Dialog from '$lib/ui/Dialog.svelte';
  import Icon from '$lib/ui/Icon.svelte';
  import ProgressBar from '$lib/ui/ProgressBar.svelte';
  import Select from '$lib/ui/Select.svelte';
  import PlatformBadge from './PlatformBadge.svelte';
  import type { Account } from '$lib/types/api';

  let { account }: { account: Account } = $props();

  let months = $state('');
  let syncing = $state(false);
  let confirmDelete = $state(false);
  let deleting = $state(false);

  const job = $derived(jobs.forAccount(account.id));
  const monthOptions = [
    { value: '', label: 'Everything new' },
    { value: '1', label: 'Last month' },
    { value: '3', label: 'Last 3 months' },
    { value: '12', label: 'Last 12 months' },
  ];

  async function sync() {
    syncing = true;
    try {
      const j = await api.syncAccount(account.id, months ? Number(months) : null);
      jobs.applyEvent(j);
    } catch (e) {
      toasts.error(errorMessage(e));
    } finally {
      syncing = false;
    }
  }

  async function remove() {
    deleting = true;
    try {
      await accounts.remove(account.id);
      toasts.info(`Removed ${account.username} and its games`);
      confirmDelete = false;
    } catch (e) {
      toasts.error(errorMessage(e));
    } finally {
      deleting = false;
    }
  }
</script>

<article class="acct">
  <header>
    <div class="who">
      <span class="name">{account.username}</span>
      <PlatformBadge platform={account.platform} size="sm" />
    </div>
    <button class="del" onclick={() => (confirmDelete = true)} title="Remove account" aria-label="Remove account"><Icon name="trash" size={16} /></button>
  </header>

  <dl class="stats">
    <div><dt>Games</dt><dd class="mono">{account.game_count.toLocaleString()}</dd></div>
    <div><dt>Analysed</dt><dd class="mono">{account.analyzed_count.toLocaleString()}</dd></div>
    <div><dt>Last sync</dt><dd>{timeAgo(account.last_synced_at)}</dd></div>
  </dl>

  {#if job}
    <div class="progress">
      <ProgressBar value={job.progress} max={job.total} tone="info" />
      <span class="muted small">{job.status === 'queued' ? 'Waiting…' : (job.message ?? 'Syncing…')}</span>
    </div>
  {:else}
    <div class="actions">
      <Select bind:value={months} options={monthOptions} size="sm" />
      <Button size="sm" variant="primary" onclick={sync} loading={syncing}><Icon name="sync" size={14} />Sync</Button>
    </div>
  {/if}
</article>

<Dialog bind:open={confirmDelete} title="Remove {account.username}?" confirmLabel="Remove" danger busy={deleting} onconfirm={remove}>
  This deletes the account link and all {pluralize(account.game_count, 'imported game')} along with their analyses. Your games stay on {account.platform === 'chesscom' ? 'Chess.com' : 'Lichess'}.
</Dialog>

<style>
  .acct {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: var(--sp-4);
    display: grid;
    gap: var(--sp-3);
  }
  header { display: flex; justify-content: space-between; align-items: center; gap: var(--sp-2); }
  .who { display: flex; align-items: center; gap: var(--sp-2); min-width: 0; }
  .name { font-weight: 600; font-size: var(--fs-lg); overflow: hidden; text-overflow: ellipsis; }
  .del { color: var(--text-faint); display: inline-flex; padding: 4px; border-radius: var(--radius); }
  .del:hover { color: var(--danger); background: var(--danger-soft); }
  .stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--sp-2);
    margin: 0;
  }
  dt { font-size: var(--fs-xs); color: var(--text-muted); }
  dd { margin: 0; font-weight: 600; }
  .actions { display: flex; gap: var(--sp-2); align-items: center; }
  .progress { display: grid; gap: 6px; }
  .small { font-size: var(--fs-xs); }
</style>
