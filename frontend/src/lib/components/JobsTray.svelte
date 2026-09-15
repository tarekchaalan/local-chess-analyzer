<script lang="ts">
  import { jobs } from '$lib/stores/jobs.svelte';
  import { accounts } from '$lib/stores/accounts.svelte';
  import { toasts } from '$lib/stores/toasts.svelte';
  import ProgressBar from '$lib/ui/ProgressBar.svelte';
  import Icon from '$lib/ui/Icon.svelte';
  import type { Job } from '$lib/types/api';

  const active = $derived(jobs.active);
  const running = $derived(active.filter((j) => j.status === 'running'));
  const queued = $derived(active.filter((j) => j.status === 'queued'));

  function label(job: Job): string {
    if (job.kind === 'sync') {
      const a = accounts.byId(job.account_id);
      return a ? `Syncing ${a.username}` : 'Syncing';
    }
    return `Analyzing game #${job.game_id}`;
  }

  async function cancel(job: Job) {
    try {
      await jobs.cancel(job.id);
    } catch (e) {
      toasts.error((e as Error).message);
    }
  }

  async function cancelAll() {
    try {
      const n = await jobs.cancelAll();
      toasts.info(`Cancelled ${n} job${n === 1 ? '' : 's'}`);
    } catch (e) {
      toasts.error((e as Error).message);
    }
  }
</script>

<div class="tray" aria-live="polite">
  {#if active.length === 0}
    <div class="idle muted">
      <Icon name="check" size={14} />
      <span>Engine idle</span>
    </div>
  {:else}
    <div class="head">
      <span class="title">{running.length} running · {queued.length} queued</span>
      <button class="link" onclick={cancelAll}>Cancel all</button>
    </div>
    {#each running as job (job.id)}
      <div class="job">
        <div class="row">
          <span class="name">{label(job)}</span>
          <button class="icon" onclick={() => cancel(job)} title="Cancel" aria-label="Cancel job"><Icon name="x" size={14} /></button>
        </div>
        <ProgressBar value={job.progress} max={job.total} tone={job.kind === 'sync' ? 'info' : 'accent'} height={4} />
        {#if job.message}<span class="msg muted">{job.message}</span>{/if}
      </div>
    {/each}
  {/if}
</div>

<style>
  .tray {
    border-top: 1px solid var(--border);
    padding: var(--sp-3) var(--sp-3);
    display: grid;
    gap: var(--sp-2);
    font-size: var(--fs-xs);
  }
  .idle { display: flex; align-items: center; gap: 6px; }
  .head { display: flex; justify-content: space-between; align-items: center; }
  .title { color: var(--text-muted); font-weight: 500; }
  .link { color: var(--text-muted); text-decoration: underline; }
  .link:hover { color: var(--text); }
  .job { display: grid; gap: 4px; }
  .row { display: flex; justify-content: space-between; align-items: center; gap: 6px; }
  .name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .icon { color: var(--text-muted); display: inline-flex; }
  .icon:hover { color: var(--text); }
  .msg { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
