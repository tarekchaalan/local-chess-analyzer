<script lang="ts">
  import { accounts } from '$lib/stores/accounts.svelte';
  import { toasts } from '$lib/stores/toasts.svelte';
  import { ApiError } from '$lib/api/client';
  import Button from '$lib/ui/Button.svelte';
  import Input from '$lib/ui/Input.svelte';
  import Select from '$lib/ui/Select.svelte';
  import type { Account, Platform } from '$lib/types/api';

  let { onadded, compact = false }: { onadded?: (a: Account) => void; compact?: boolean } = $props();

  let platform = $state<Platform>('chesscom');
  let username = $state('');
  let busy = $state(false);
  let error = $state<string | null>(null);

  async function submit(e: Event) {
    e.preventDefault();
    const name = username.trim();
    if (!name) return;
    busy = true;
    error = null;
    try {
      const account = await accounts.add(platform, name);
      username = '';
      toasts.success(`Linked ${account.username} on ${platform === 'chesscom' ? 'Chess.com' : 'Lichess'}`);
      onadded?.(account);
    } catch (e) {
      if (e instanceof ApiError && (e.code === 'user_not_found' || e.code === 'already_linked')) error = e.message;
      else if (e instanceof ApiError) error = `${e.message} (${e.code})`;
      else error = (e as Error).message;
    } finally {
      busy = false;
    }
  }
</script>

<form class="form" class:compact onsubmit={submit}>
  <div class="row">
    <Select
      label="Platform"
      bind:value={platform}
      options={[
        { value: 'chesscom', label: 'Chess.com' },
        { value: 'lichess', label: 'Lichess' },
      ]}
    />
    <Input label="Username" bind:value={username} placeholder={platform === 'chesscom' ? 'e.g. hikaru' : 'e.g. DrNykterstein'} {error} disabled={busy} />
    <div class="submit">
      <Button type="submit" variant="primary" loading={busy} disabled={!username.trim()}>Link account</Button>
    </div>
  </div>
</form>

<style>
  .row {
    display: grid;
    grid-template-columns: 160px 1fr auto;
    gap: var(--sp-3);
    align-items: end;
  }
  .submit { padding-bottom: 0; }
  @media (max-width: 640px) {
    .row { grid-template-columns: 1fr; }
  }
</style>
