<script lang="ts">
  import Icon from '$lib/ui/Icon.svelte';
  import { jobs } from '$lib/stores/jobs.svelte';
  import Logo from '$lib/ui/Logo.svelte';

  let { onmenu }: { onmenu: () => void } = $props();
  const active = $derived(jobs.active.length);
</script>

<header class="topbar">
  <button class="menu" onclick={onmenu} aria-label="Open menu"><Icon name="menu" /></button>
  <a class="brand" href="#/"><Logo size={22} /> Local Chess Analyzer</a>
  {#if active > 0}<span class="pill">{active} job{active === 1 ? '' : 's'}</span>{/if}
</header>

<style>
  .topbar {
    display: flex;
    align-items: center;
    gap: var(--sp-3);
    height: var(--topbar-h);
    padding: 0 var(--sp-3);
    padding-top: env(safe-area-inset-top, 0px);
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 20;
  }
  .menu { display: inline-flex; color: var(--text-muted); padding: 6px; }
  .brand { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: var(--fs-sm); }
  .pill {
    margin-left: auto;
    font-size: var(--fs-xs);
    padding: 2px 8px;
    border-radius: 999px;
    background: var(--accent-soft);
    color: var(--accent);
  }
</style>
