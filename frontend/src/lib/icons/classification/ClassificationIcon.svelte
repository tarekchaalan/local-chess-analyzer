<script lang="ts">
  import { CLASSIFICATIONS } from '$lib/chess/classification';
  import type { Classification } from '$lib/types/api';

  let { label, size = 20, class: cls = '' }: { label: Classification; size?: number; class?: string } = $props();
  const meta = $derived(CLASSIFICATIONS[label]);
  const textGlyph = $derived(!['best', 'excellent', 'good', 'book', 'miss', 'forced'].includes(label));
</script>

<svg
  class="cicon {cls}"
  width={size}
  height={size}
  viewBox="0 0 24 24"
  role="img"
  aria-label={meta.label}
  style="--c:{meta.color}"
>
  <circle cx="12" cy="12" r="11" fill="var(--c)" />
  {#if label === 'best'}
    <path d="M12 4.6l2.2 4.6 5 .7-3.6 3.5.9 5L12 16l-4.5 2.4.9-5L4.8 9.9l5-.7z" fill="#fff" />
  {:else if label === 'excellent'}
    <path d="M6.5 12.5l3.5 3.5 7.5-8" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" />
    <path d="M6.5 8.5l2 2" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" />
  {:else if label === 'good'}
    <path d="M6.5 12.5l3.5 3.5 7.5-8" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" />
  {:else if label === 'book'}
    <path d="M6 6.5c2-.6 4-.4 6 .7 2-1.1 4-1.3 6-.7v10.4c-2-.6-4-.4-6 .7-2-1.1-4-1.3-6-.7z" fill="none" stroke="#fff" stroke-width="1.8" stroke-linejoin="round" />
    <path d="M12 7.2v10.4" stroke="#fff" stroke-width="1.6" />
  {:else if label === 'miss'}
    <path d="M8 8l8 8M16 8l-8 8" fill="none" stroke="#fff" stroke-width="2.8" stroke-linecap="round" />
  {:else if label === 'forced'}
    <path d="M6 12h11M13 8l4 4-4 4" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" />
  {:else if textGlyph}
    <text x="12" y="17.2" text-anchor="middle" font-size={meta.symbol.length > 1 ? 12.5 : 15} font-weight="800" fill="#fff" font-family="var(--font)">{meta.symbol}</text>
  {/if}
</svg>

<style>
  .cicon {
    display: inline-block;
    vertical-align: middle;
    flex: none;
  }
</style>
