<script lang="ts">
  import { matchRoute, router, type RouteDef } from './routing.svelte';
  import type { Component } from 'svelte';

  let { routes, fallback }: { routes: RouteDef[]; fallback: Component<any> } = $props();

  const match = $derived(matchRoute(routes, router.path));
  const Page = $derived(match?.component ?? fallback);
  const params = $derived(match?.params ?? {});
</script>

{#key router.path}
  <Page {...params} />
{/key}
