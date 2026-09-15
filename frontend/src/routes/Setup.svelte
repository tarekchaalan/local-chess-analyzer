<script lang="ts">
  import { navigate } from '$lib/router/routing.svelte';
  import { accounts } from '$lib/stores/accounts.svelte';
  import { jobs } from '$lib/stores/jobs.svelte';
  import { settings } from '$lib/stores/settings.svelte';
  import { toasts } from '$lib/stores/toasts.svelte';
  import { api } from '$lib/api/client';
  import { errorMessage } from '$lib/format';
  import AddAccountForm from '$lib/components/AddAccountForm.svelte';
  import EngineTuning from '$lib/components/EngineTuning.svelte';
  import PlatformBadge from '$lib/components/PlatformBadge.svelte';
  import Button from '$lib/ui/Button.svelte';
  import Icon from '$lib/ui/Icon.svelte';
  import ProgressBar from '$lib/ui/ProgressBar.svelte';
  import Logo from '$lib/ui/Logo.svelte';

  let step = $state(accounts.list.length > 0 ? 2 : 1);
  let syncStarted = $state(false);

  const steps = ['Link an account', 'Tune the engine', 'Import games'];
  const syncJobs = $derived(jobs.list.filter((j) => j.kind === 'sync'));
  const syncDone = $derived(syncStarted && syncJobs.length > 0 && syncJobs.every((j) => j.status !== 'queued' && j.status !== 'running'));
  const totalGames = $derived(accounts.list.reduce((n, a) => n + a.game_count, 0));

  async function startSync() {
    syncStarted = true;
    try {
      const js = await api.syncAll();
      js.forEach((j) => jobs.applyEvent(j));
    } catch (e) {
      toasts.error(errorMessage(e));
      syncStarted = false;
    }
  }

  async function finish(target = '/games') {
    try {
      await settings.update({ setup_completed: true });
    } catch (e) {
      toasts.error(errorMessage(e));
    }
    navigate(target);
  }
</script>

<div class="setup">
  <div class="panel">
    <header>
      <Logo size={40} />
      <div>
        <h1>Welcome</h1>
        <p class="muted">Private game review for your chess.com and Lichess games. Nothing leaves this machine.</p>
      </div>
    </header>

    <ol class="stepper">
      {#each steps as label, i (label)}
        <li class:active={step === i + 1} class:done={step > i + 1}>
          <span class="num">{#if step > i + 1}<Icon name="check" size={12} />{:else}{i + 1}{/if}</span>
          <span>{label}</span>
        </li>
      {/each}
    </ol>

    {#if step === 1}
      <section>
        <h2>Link your first account</h2>
        <p class="muted">Enter a username on either platform. You can add more later from the Accounts page.</p>
        <AddAccountForm onadded={() => (step = 2)} />
        <div class="foot">
          <button class="skip" onclick={() => finish('/accounts')}>Skip setup</button>
        </div>
      </section>
    {:else if step === 2}
      <section>
        <h2>Tune the engine</h2>
        <p class="muted">These defaults are recommended for this computer. Deeper analysis is slower but more accurate.</p>
        <EngineTuning showPath={false} onsaved={() => (step = 3)} />
        <div class="foot">
          <button class="skip" onclick={() => (step = 3)}>Keep defaults</button>
        </div>
      </section>
    {:else}
      <section>
        <h2>Import your games</h2>
        <div class="linked">
          {#each accounts.list as a (a.id)}
            <div class="row">
              <span class="name">{a.username}</span>
              <PlatformBadge platform={a.platform} size="sm" />
              {#if syncStarted}
                {@const job = jobs.forAccount(a.id)}
                <span class="prog">
                  {#if job}
                    <ProgressBar value={job.progress} max={job.total} tone="info" height={5} />
                    <span class="muted small">{job.message ?? (job.status === 'queued' ? 'Waiting…' : 'Starting…')}</span>
                  {:else}
                    <span class="muted small">{a.game_count.toLocaleString()} games</span>
                  {/if}
                </span>
              {/if}
            </div>
          {/each}
        </div>
        {#if !syncStarted}
          <p class="muted">This fetches every game on each account. Large accounts can take a few minutes.</p>
          <div class="foot">
            <Button variant="primary" onclick={startSync}><Icon name="sync" size={14} />Start import</Button>
            <button class="skip" onclick={() => finish('/accounts')}>Later</button>
          </div>
        {:else if syncDone}
          <p class="done"><Icon name="check" size={16} /> Imported {totalGames.toLocaleString()} games.</p>
          <div class="foot">
            <Button variant="primary" onclick={() => finish('/games')}>Go to games</Button>
          </div>
        {:else}
          <div class="foot">
            <button class="skip" onclick={() => finish('/games')}>Continue in background</button>
          </div>
        {/if}
      </section>
    {/if}
  </div>
</div>

<style>
  .setup { display: grid; place-items: start center; min-height: 100vh; padding: var(--sp-6) var(--sp-4); }
  .panel {
    width: min(100%, 640px);
    display: grid;
    gap: var(--sp-5);
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: var(--sp-6);
  }
  header { display: flex; gap: var(--sp-4); align-items: center; }
  header p { margin-top: 4px; }
  .stepper {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--sp-2);
    list-style: none;
    margin: 0;
    padding: 0;
    font-size: var(--fs-xs);
    color: var(--text-faint);
  }
  .stepper li { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-top: 2px solid var(--border); }
  .stepper li.active { color: var(--text); border-top-color: var(--accent); }
  .stepper li.done { color: var(--text-muted); border-top-color: var(--accent); }
  .num {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: inline-grid;
    place-items: center;
    background: var(--raised);
    font-weight: 600;
  }
  .active .num { background: var(--accent); color: var(--on-accent); }
  .done .num { background: var(--accent-soft); color: var(--accent); }
  section { display: grid; gap: var(--sp-4); }
  section h2 { font-size: var(--fs-xl); }
  .foot { display: flex; align-items: center; gap: var(--sp-4); }
  .skip { color: var(--text-muted); font-size: var(--fs-sm); text-decoration: underline; }
  .skip:hover { color: var(--text); }
  .linked { display: grid; gap: var(--sp-2); }
  .row { display: grid; grid-template-columns: auto auto 1fr; gap: var(--sp-3); align-items: center; padding: 10px 12px; border: 1px solid var(--border); border-radius: var(--radius); }
  .name { font-weight: 600; }
  .prog { display: grid; gap: 4px; }
  .small { font-size: var(--fs-xs); }
  .done { display: flex; align-items: center; gap: 8px; color: var(--accent); font-weight: 500; }
</style>
