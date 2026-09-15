<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api/client';
  import { settings } from '$lib/stores/settings.svelte';
  import { toasts } from '$lib/stores/toasts.svelte';
  import { errorMessage } from '$lib/format';
  import Button from '$lib/ui/Button.svelte';
  import Input from '$lib/ui/Input.svelte';
  import Badge from '$lib/ui/Badge.svelte';
  import Icon from '$lib/ui/Icon.svelte';
  import Skeleton from '$lib/ui/Skeleton.svelte';
  import type { SystemInfo } from '$lib/types/api';

  let { onsaved, showPath = true }: { onsaved?: () => void; showPath?: boolean } = $props();

  let sys = $state<SystemInfo | null>(null);
  let path = $state(settings.get('engine_path'));
  let threads = $state(settings.get('engine_threads'));
  let hash = $state(settings.get('engine_hash_mb'));
  let depth = $state(settings.get('analysis_depth'));
  let timeMs = $state(settings.get('analysis_time_ms'));
  let validating = $state(false);
  let validation = $state<SystemInfo['engine'] | null>(null);
  let saving = $state(false);

  onMount(async () => {
    try {
      sys = await api.system();
      validation = sys.engine;
    } catch (e) {
      toasts.error(errorMessage(e));
    }
  });

  function useRecommended() {
    if (!sys) return;
    threads = String(sys.cpu.recommended_threads);
    hash = String(sys.memory.recommended_hash_mb);
    depth = String(sys.recommended_depth);
  }

  async function validate() {
    validating = true;
    try {
      validation = await api.validateEngine(path);
    } catch (e) {
      toasts.error(errorMessage(e));
    } finally {
      validating = false;
    }
  }

  async function save() {
    saving = true;
    try {
      await settings.update({
        engine_path: path,
        engine_threads: threads,
        engine_hash_mb: hash,
        analysis_depth: depth,
        analysis_time_ms: timeMs,
      });
      toasts.success('Engine settings saved');
      onsaved?.();
    } catch (e) {
      toasts.error(errorMessage(e));
    } finally {
      saving = false;
    }
  }

  const estimate = $derived.by(() => {
    const d = Number(depth);
    const t = Number(timeMs);
    const perPly = t > 0 ? Math.min(t / 1000, 0.08 * 1.35 ** (d - 10)) : 0.08 * 1.35 ** (d - 10);
    const secs = perPly * 80;
    return secs < 60 ? `~${Math.max(5, Math.round(secs))}s per game` : `~${(secs / 60).toFixed(1)} min per game`;
  });
</script>

<div class="tuning">
  {#if !sys}
    <Skeleton height="60px" />
  {:else}
    <div class="host muted">
      <span><Icon name="info" size={14} /> {sys.platform}</span>
      <span>{sys.cpu.logical_cores} threads · {(sys.memory.total_mb / 1024).toFixed(0)} GB RAM</span>
      <button class="link" onclick={useRecommended}>Use recommended</button>
    </div>
  {/if}

  {#if showPath}
    <div class="path">
      <Input label="Stockfish binary" bind:value={path} mono hint="Bundled Stockfish is auto-detected. Point this at another UCI engine to use it instead." />
      <div class="validate">
        <Button size="sm" onclick={validate} loading={validating}>Validate</Button>
        {#if validation}
          <Badge tone={validation.valid ? 'success' : 'danger'}>{validation.valid ? validation.name : validation.message}</Badge>
        {/if}
      </div>
    </div>
  {/if}

  <div class="grid">
    <Input label="Threads" type="number" bind:value={threads} min={1} max={128} hint={sys ? `recommended ${sys.cpu.recommended_threads}` : ''} />
    <Input label="Hash (MB)" type="number" bind:value={hash} min={16} max={16384} hint={sys ? `recommended ${sys.memory.recommended_hash_mb}` : ''} />
    <Input label="Depth" type="number" bind:value={depth} min={1} max={60} hint={sys ? `recommended ${sys.recommended_depth}` : ''} />
    <Input label="Time cap per move (ms)" type="number" bind:value={timeMs} min={0} max={600000} hint="0 = depth only" />
  </div>

  <div class="foot">
    <span class="muted small">{estimate} at these settings</span>
    <Button variant="primary" onclick={save} loading={saving}>Save engine settings</Button>
  </div>
</div>

<style>
  .tuning { display: grid; gap: var(--sp-4); }
  .host { display: flex; gap: var(--sp-4); align-items: center; font-size: var(--fs-xs); flex-wrap: wrap; }
  .host span { display: inline-flex; align-items: center; gap: 6px; }
  .link { color: var(--accent); font-weight: 500; margin-left: auto; }
  .path { display: grid; gap: var(--sp-2); }
  .validate { display: flex; align-items: center; gap: var(--sp-2); flex-wrap: wrap; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: var(--sp-3); }
  .foot { display: flex; justify-content: space-between; align-items: center; gap: var(--sp-3); flex-wrap: wrap; }
  .small { font-size: var(--fs-xs); }
</style>
