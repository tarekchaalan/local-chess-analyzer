<script lang="ts">
  import type { Snippet } from 'svelte';
  import Icon, { type IconName } from './Icon.svelte';

  let {
    title,
    description,
    icon = 'info',
    children,
  }: { title: string; description?: string; icon?: IconName; children?: Snippet } = $props();
</script>

<div class="empty">
  <div class="icon"><Icon name={icon} size={22} /></div>
  <h3>{title}</h3>
  {#if description}<p class="muted">{description}</p>{/if}
  {#if children}<div class="actions">{@render children()}</div>{/if}
</div>

<style>
  .empty {
    display: grid;
    justify-items: center;
    gap: var(--sp-2);
    padding: var(--sp-6) var(--sp-4);
    text-align: center;
    max-width: 420px;
    margin: 0 auto;
  }
  .icon {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    background: var(--raised);
    color: var(--text-muted);
    margin-bottom: var(--sp-1);
  }
  .actions { margin-top: var(--sp-2); display: flex; gap: var(--sp-2); }
</style>
