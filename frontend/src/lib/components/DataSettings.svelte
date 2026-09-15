<script lang="ts">
  import { api } from '$lib/api/client';
  import { accounts } from '$lib/stores/accounts.svelte';
  import { jobs } from '$lib/stores/jobs.svelte';
  import { settings } from '$lib/stores/settings.svelte';
  import { toasts } from '$lib/stores/toasts.svelte';
  import { errorMessage } from '$lib/format';
  import Button from '$lib/ui/Button.svelte';
  import Dialog from '$lib/ui/Dialog.svelte';
  import Icon from '$lib/ui/Icon.svelte';

  let importFile = $state<File | null>(null);
  let confirmImport = $state(false);
  let confirmReset = $state(false);
  let busy = $state(false);
  let fileInput = $state<HTMLInputElement>();

  function pick(e: Event) {
    const f = (e.target as HTMLInputElement).files?.[0] ?? null;
    if (f) {
      importFile = f;
      confirmImport = true;
    }
  }

  async function doImport() {
    if (!importFile) return;
    busy = true;
    try {
      const res = await api.importDatabase(importFile);
      toasts.success(`Imported ${res.games.toLocaleString()} games and ${res.accounts} account${res.accounts === 1 ? '' : 's'}`);
      confirmImport = false;
      await Promise.all([accounts.refresh(), jobs.load(), settings.load()]);
    } catch (e) {
      toasts.error(errorMessage(e));
    } finally {
      busy = false;
      importFile = null;
      if (fileInput) fileInput.value = '';
    }
  }

  async function doReset() {
    busy = true;
    try {
      const res = await api.resetDatabase();
      toasts.info(`Deleted ${res.deleted_games.toLocaleString()} games`);
      confirmReset = false;
      await Promise.all([accounts.refresh(), jobs.load()]);
    } catch (e) {
      toasts.error(errorMessage(e));
    } finally {
      busy = false;
    }
  }
</script>

<div class="data">
  <div class="row">
    <div>
      <strong>Export database</strong>
      <p class="muted small">Download a snapshot of every game, analysis and setting as a single SQLite file.</p>
    </div>
    <Button href={api.exportUrl()}><Icon name="download" size={14} />Export</Button>
  </div>
  <div class="row">
    <div>
      <strong>Import database</strong>
      <p class="muted small">Replace the current library with an exported file. A backup of the current file is kept next to it.</p>
    </div>
    <label class="file">
      <input bind:this={fileInput} type="file" accept=".db,.sqlite,application/vnd.sqlite3" onchange={pick} />
      <span class="btn-like"><Icon name="upload" size={14} />Import…</span>
    </label>
  </div>
  <div class="row danger">
    <div>
      <strong>Reset library</strong>
      <p class="muted small">Delete all accounts, games and analyses. Settings are kept.</p>
    </div>
    <Button variant="danger" onclick={() => (confirmReset = true)}><Icon name="trash" size={14} />Reset</Button>
  </div>
</div>

<Dialog bind:open={confirmImport} title="Replace the library?" confirmLabel="Import" {busy} onconfirm={doImport} oncancel={() => { importFile = null; if (fileInput) fileInput.value = ''; }}>
  Everything currently in the library will be replaced by <strong>{importFile?.name}</strong>. Running jobs are cancelled first and a backup of the current file is written alongside it.
</Dialog>

<Dialog bind:open={confirmReset} title="Delete everything?" confirmLabel="Delete all data" danger {busy} onconfirm={doReset}>
  This removes every linked account, imported game and analysis from this computer. Your games stay on Chess.com and Lichess and can be re-imported.
</Dialog>

<style>
  .data { display: grid; }
  .row { display: flex; justify-content: space-between; align-items: center; gap: var(--sp-4); padding: var(--sp-3) 0; border-top: 1px solid var(--border); }
  .row:first-child { border-top: 0; padding-top: 0; }
  .small { font-size: var(--fs-xs); margin-top: 2px; max-width: 52ch; }
  .file input { position: absolute; width: 1px; height: 1px; opacity: 0; }
  .file { position: relative; }
  .btn-like {
    display: inline-flex; align-items: center; gap: var(--sp-2); height: 36px; padding: 0 var(--sp-4);
    border-radius: var(--radius); border: 1px solid var(--border-strong); background: var(--raised);
    font-size: var(--fs-sm); font-weight: 500; cursor: pointer;
  }
  .file:focus-within .btn-like { box-shadow: var(--focus); }
</style>
