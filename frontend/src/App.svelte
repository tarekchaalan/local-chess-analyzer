<script lang="ts">
  import { onMount } from 'svelte';
  import Router from '$lib/router/Router.svelte';
  import { navigate, router } from '$lib/router/routing.svelte';
  import { connectEvents } from '$lib/api/sse';
  import { settings } from '$lib/stores/settings.svelte';
  import { accounts } from '$lib/stores/accounts.svelte';
  import { jobs } from '$lib/stores/jobs.svelte';
  import { toasts } from '$lib/stores/toasts.svelte';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import TopBar from '$lib/components/TopBar.svelte';
  import Toasts from '$lib/ui/Toasts.svelte';
  import Icon from '$lib/ui/Icon.svelte';
  import NotFound from './routes/NotFound.svelte';
  import Dashboard from './routes/Dashboard.svelte';
  import Settings from './routes/Settings.svelte';
  import Accounts from './routes/Accounts.svelte';
  import Games from './routes/Games.svelte';
  import GameReview from './routes/GameReview.svelte';
  import Setup from './routes/Setup.svelte';

  const routes = [
    { path: '/', component: Dashboard },
    { path: '/games', component: Games },
    { path: '/games/:id', component: GameReview },
    { path: '/accounts', component: Accounts },
    { path: '/settings', component: Settings },
    { path: '/setup', component: Setup },
  ];

  let ready = $state(false);
  let offline = $state(false);
  let menuOpen = $state(false);

  const inSetup = $derived(router.path === '/setup');

  let offlineTimer: ReturnType<typeof setTimeout> | null = null;

  onMount(() => {
    let disconnect = () => {};
    (async () => {
      try {
        await Promise.all([settings.load(), accounts.load(), jobs.load()]);
        if (accounts.list.length === 0 && !settings.bool('setup_completed') && router.path !== '/setup') {
          navigate('/setup');
        }
      } catch (e) {
        offline = true;
        toasts.error(`Could not reach the server: ${(e as Error).message}`);
      } finally {
        ready = true;
      }
      disconnect = connectEvents({
        job: (job) => jobs.applyEvent(job),
        account: (ev) => accounts.applyEvent(ev),
        open: () => {
          if (offlineTimer) clearTimeout(offlineTimer);
          offlineTimer = null;
          offline = false;
          jobs.load().catch(() => {});
        },
        close: () => {
          // Only warn if the stream stays down for a while; reconnects are normal.
          if (!offlineTimer) offlineTimer = setTimeout(() => (offline = true), 4000);
        },
      });
    })();
    return () => disconnect();
  });
</script>

<Toasts />

{#if !ready}
  <div class="boot muted">Loading…</div>
{:else}
  <div class="app" class:setup={inSetup}>
    {#if !inSetup}
      <div class="side" class:open={menuOpen}>
        <Sidebar onnavigate={() => (menuOpen = false)} />
      </div>
      {#if menuOpen}
        <button class="scrim" aria-label="Close menu" onclick={() => (menuOpen = false)}></button>
      {/if}
      <div class="top"><TopBar onmenu={() => (menuOpen = true)} /></div>
    {/if}
    <main class="main">
      {#if offline}
        <div class="offline"><Icon name="warning" size={14} /> Connection to the server lost — retrying…</div>
      {/if}
      <Router {routes} fallback={NotFound} />
    </main>
  </div>
{/if}

<style>
  .boot { display: grid; place-items: center; min-height: 100vh; }
  .app {
    display: grid;
    grid-template-columns: var(--sidebar-w) 1fr;
    min-height: 100vh;
  }
  .app.setup { grid-template-columns: 1fr; }
  .side {
    position: sticky;
    top: 0;
    height: 100vh;
  }
  .top { display: none; }
  .main {
    min-width: 0;
    padding: var(--sp-5) var(--sp-5) calc(var(--sp-6) + env(safe-area-inset-bottom, 0px));
    padding-top: calc(var(--sp-5) + env(safe-area-inset-top, 0px));
  }
  .offline {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-bottom: var(--sp-3);
    padding: 6px 10px;
    border-radius: var(--radius);
    background: rgba(247, 198, 49, 0.12);
    color: var(--warning);
    font-size: var(--fs-xs);
  }
  .scrim {
    display: none;
  }
  @media (max-width: 900px) {
    .app { grid-template-columns: 1fr; }
    .top { display: block; grid-row: 1; }
    .side {
      position: fixed;
      inset: 0 auto 0 0;
      width: min(80vw, 280px);
      z-index: 30;
      transform: translateX(-100%);
      transition: transform 200ms var(--ease);
      box-shadow: var(--shadow);
    }
    .side.open { transform: none; }
    .scrim {
      display: block;
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.5);
      z-index: 25;
    }
    .main { padding: var(--sp-4); }
  }
</style>
