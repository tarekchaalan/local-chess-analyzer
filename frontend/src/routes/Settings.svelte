<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api/client';
  import { settings } from '$lib/stores/settings.svelte';
  import { toasts } from '$lib/stores/toasts.svelte';
  import { errorMessage } from '$lib/format';
  import EngineTuning from '$lib/components/EngineTuning.svelte';
  import DataSettings from '$lib/components/DataSettings.svelte';
  import Card from '$lib/ui/Card.svelte';
  import Input from '$lib/ui/Input.svelte';
  import Button from '$lib/ui/Button.svelte';
  import Tabs from '$lib/ui/Tabs.svelte';

  let theme = $state(settings.get('theme', 'system'));
  let autoAnalyze = $state(settings.bool('auto_analyze_new_games'));
  let moveSounds = $state(settings.bool('move_sounds'));
  let lichessToken = $state(settings.get('lichess_token'));
  let savingToken = $state(false);
  let version = $state('');

  onMount(async () => {
    try {
      version = (await api.health()).version;
    } catch {
      /* non-fatal */
    }
  });

  async function saveTheme(v: string) {
    try {
      await settings.update({ theme: v });
    } catch (e) {
      toasts.error(errorMessage(e));
    }
  }

  async function saveAuto() {
    try {
      await settings.update({ auto_analyze_new_games: autoAnalyze });
      toasts.success(autoAnalyze ? 'New games will be analysed automatically' : 'Automatic analysis off');
    } catch (e) {
      toasts.error(errorMessage(e));
      autoAnalyze = !autoAnalyze;
    }
  }

  async function saveSounds() {
    try {
      await settings.update({ move_sounds: moveSounds });
    } catch (e) {
      toasts.error(errorMessage(e));
      moveSounds = !moveSounds;
    }
  }

  async function saveToken() {
    savingToken = true;
    try {
      await settings.update({ lichess_token: lichessToken });
      toasts.success('Lichess token saved');
    } catch (e) {
      toasts.error(errorMessage(e));
    } finally {
      savingToken = false;
    }
  }
</script>

<div class="page">
  <h1>Settings</h1>

  <Card title="Engine" subtitle="Stockfish settings used for every analysis">
    <EngineTuning />
  </Card>

  <Card title="Behaviour">
    <div class="toggles">
      <label class="toggle">
        <input type="checkbox" bind:checked={autoAnalyze} onchange={saveAuto} />
        <span>
          <strong>Analyse new games automatically</strong>
          <span class="muted small">Every game imported by a sync is queued for analysis.</span>
        </span>
      </label>
      <label class="toggle">
        <input type="checkbox" bind:checked={moveSounds} onchange={saveSounds} />
        <span>
          <strong>Move sounds</strong>
          <span class="muted small">Play a sound when stepping through a game. Press M in a review to toggle.</span>
        </span>
      </label>
    </div>
  </Card>

  <Card title="Appearance">
    <div class="row">
      <span>Theme</span>
      <Tabs bind:value={theme} options={[{ value: 'system', label: 'System' }, { value: 'dark', label: 'Dark' }, { value: 'light', label: 'Light' }]} onchange={saveTheme} />
    </div>
  </Card>

  <Card title="Lichess" subtitle="Optional personal API token — raises the download rate limit for large accounts">
    <div class="token">
      <Input type="password" bind:value={lichessToken} placeholder="lip_…" mono hint="Create one at lichess.org/account/oauth/token — no scopes are required." />
      <Button onclick={saveToken} loading={savingToken}>Save</Button>
    </div>
  </Card>

  <Card title="Data">
    <DataSettings />
  </Card>

  <p class="muted small about">Local Chess Analyzer {version ? `v${version}` : ''} · Stockfish is GPL-3.0 · opening names from the Lichess chess-openings dataset (CC0).</p>
</div>

<style>
  .page { display: grid; gap: var(--sp-4); max-width: 860px; }
  .toggles { display: grid; gap: var(--sp-4); }
  .toggle { display: flex; gap: var(--sp-3); align-items: flex-start; cursor: pointer; }
  .toggle input { accent-color: var(--accent); width: 16px; height: 16px; margin-top: 3px; }
  .toggle span { display: grid; }
  .small { font-size: var(--fs-xs); }
  .row { display: flex; justify-content: space-between; align-items: center; gap: var(--sp-3); }
  .token { display: grid; grid-template-columns: 1fr auto; gap: var(--sp-2); align-items: start; }
  .about { text-align: center; padding: var(--sp-3) 0; }
</style>
