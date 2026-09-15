<script lang="ts">
  import type { Snippet } from 'svelte';

  let {
    title,
    subtitle,
    actions,
    padded = true,
    class: cls = '',
    children,
  }: {
    title?: string;
    subtitle?: string;
    actions?: Snippet;
    padded?: boolean;
    class?: string;
    children: Snippet;
  } = $props();
</script>

<section class="card {cls}" class:padded>
  {#if title || actions}
    <header class="head">
      <div>
        {#if title}<h3>{title}</h3>{/if}
        {#if subtitle}<p class="muted sub">{subtitle}</p>{/if}
      </div>
      {#if actions}<div class="actions">{@render actions()}</div>{/if}
    </header>
  {/if}
  <div class="body">{@render children()}</div>
</section>

<style>
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  .head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: var(--sp-3);
    padding: var(--sp-4) var(--sp-4) 0;
  }
  .sub { font-size: var(--fs-sm); margin-top: 2px; }
  .actions { display: flex; gap: var(--sp-2); align-items: center; }
  .padded .body { padding: var(--sp-4); }
  .body { min-width: 0; }
</style>
