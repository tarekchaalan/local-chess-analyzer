<script lang="ts">
  import Icon from '$lib/ui/Icon.svelte';
  import { PLATFORM_LABEL } from '$lib/format';
  import type { Platform } from '$lib/types/api';

  let { platform, size = 'md' }: { platform: Platform; size?: 'sm' | 'md' } = $props();
</script>

<span class="pb {platform} {size}"><Icon name={platform} size={size === 'sm' ? 12 : 14} />{PLATFORM_LABEL[platform]}</span>

<style>
  .pb {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 2px 8px;
    border-radius: 999px;
    font-size: var(--fs-xs);
    font-weight: 600;
    border: 1px solid var(--border);
    background: var(--raised);
    color: var(--text-muted);
  }
  .sm { padding: 0 6px; font-size: 11px; }
  .chesscom { color: #8bc34a; }
  .lichess { color: var(--text); }
</style>
