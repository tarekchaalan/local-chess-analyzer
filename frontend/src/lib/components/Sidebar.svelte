<script lang="ts">
  import { isActive, router } from '$lib/router/routing.svelte';
  import Icon, { type IconName } from '$lib/ui/Icon.svelte';
  import JobsTray from './JobsTray.svelte';
  import logo from '../../assets/logo.svg';

  let { onnavigate }: { onnavigate?: () => void } = $props();

  const items: { path: string; label: string; icon: IconName }[] = [
    { path: '/', label: 'Dashboard', icon: 'dashboard' },
    { path: '/games', label: 'Games', icon: 'games' },
    { path: '/accounts', label: 'Accounts', icon: 'accounts' },
    { path: '/settings', label: 'Settings', icon: 'settings' },
  ];
</script>

<aside class="sidebar">
  <a class="brand" href="#/" onclick={onnavigate}>
    <img src={logo} alt="" width="28" height="28" />
    <span>Local Chess<br /><strong>Analyzer</strong></span>
  </a>
  <nav>
    {#each items as item (item.path)}
      <a href="#{item.path}" class:active={isActive(item.path, router.path)} onclick={onnavigate}>
        <Icon name={item.icon} size={18} />
        <span>{item.label}</span>
      </a>
    {/each}
  </nav>
  <div class="spacer"></div>
  <JobsTray />
</aside>

<style>
  .sidebar {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--surface);
    border-right: 1px solid var(--border);
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: var(--sp-4) var(--sp-4) var(--sp-3);
    font-size: var(--fs-xs);
    line-height: 1.15;
    color: var(--text-muted);
    text-decoration: none;
  }
  .brand strong { color: var(--text); font-size: var(--fs-sm); }
  nav { display: grid; gap: 2px; padding: var(--sp-2); }
  nav a {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: var(--radius);
    color: var(--text-muted);
    font-size: var(--fs-sm);
    font-weight: 500;
    text-decoration: none;
  }
  nav a:hover { background: var(--hover); color: var(--text); }
  nav a.active { background: var(--active); color: var(--text); }
  .spacer { flex: 1; }
</style>
