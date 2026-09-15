<script lang="ts">
  import Router from '$lib/router/Router.svelte';
  import NotFound from './routes/NotFound.svelte';
  import Placeholder from './routes/Placeholder.svelte';

  const routes = [{ path: '/', component: Placeholder }];
</script>

<Router {routes} fallback={NotFound} />
