<script lang="ts">
  import { accounts } from '$lib/stores/accounts.svelte';
  import { jobs } from '$lib/stores/jobs.svelte';
  import { toasts } from '$lib/stores/toasts.svelte';
  import { api } from '$lib/api/client';
  import { errorMessage } from '$lib/format';
  import AccountCard from '$lib/components/AccountCard.svelte';
  import AddAccountForm from '$lib/components/AddAccountForm.svelte';
  import Button from '$lib/ui/Button.svelte';
  import Card from '$lib/ui/Card.svelte';
  import EmptyState from '$lib/ui/EmptyState.svelte';
  import Icon from '$lib/ui/Icon.svelte';

  let syncingAll = $state(false);

  async function syncAll() {
    syncingAll = true;
    try {
      const js = await api.syncAll();
      js.forEach((j) => jobs.applyEvent(j));
      toasts.info(`Syncing ${js.length} account${js.length === 1 ? '' : 's'}`);
    } catch (e) {
      toasts.error(errorMessage(e));
    } finally {
      syncingAll = false;
    }
  }
</script>

<div class="page">
  <header class="head">
    <div>
      <h1>Accounts</h1>
      <p class="muted">Link any number of Chess.com and Lichess accounts. Games from all of them live in one library.</p>
    </div>
    {#if accounts.list.length > 1}
      <Button onclick={syncAll} loading={syncingAll}><Icon name="sync" size={14} />Sync all</Button>
    {/if}
  </header>

  <Card title="Link an account">
    <AddAccountForm />
  </Card>

  {#if accounts.list.length === 0}
    <EmptyState icon="accounts" title="No accounts linked yet" description="Add a username above to import its games." />
  {:else}
    <div class="grid">
      {#each accounts.list as account (account.id)}
        <AccountCard {account} />
      {/each}
    </div>
  {/if}
</div>

<style>
  .page { display: grid; gap: var(--sp-5); max-width: 1100px; }
  .head { display: flex; justify-content: space-between; align-items: flex-start; gap: var(--sp-3); flex-wrap: wrap; }
  .head p { margin-top: 4px; max-width: 60ch; }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: var(--sp-4);
  }
</style>
