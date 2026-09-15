<script lang="ts">
  import type { Snippet } from 'svelte';
  import Spinner from './Spinner.svelte';

  type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';
  let {
    variant = 'secondary',
    size = 'md',
    loading = false,
    disabled = false,
    type = 'button',
    href,
    class: cls = '',
    title,
    onclick,
    children,
  }: {
    variant?: Variant;
    size?: 'sm' | 'md';
    loading?: boolean;
    disabled?: boolean;
    type?: 'button' | 'submit';
    href?: string;
    class?: string;
    title?: string;
    onclick?: (e: MouseEvent) => void;
    children: Snippet;
  } = $props();
</script>

{#if href}
  <a {href} class="btn {variant} {size} {cls}" {title} aria-disabled={disabled || loading}>
    {#if loading}<Spinner size={14} />{/if}
    {@render children()}
  </a>
{:else}
  <button {type} class="btn {variant} {size} {cls}" disabled={disabled || loading} {title} {onclick}>
    {#if loading}<Spinner size={14} />{/if}
    {@render children()}
  </button>
{/if}

<style>
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--sp-2);
    padding: 0 var(--sp-4);
    height: 36px;
    border-radius: var(--radius);
    border: 1px solid transparent;
    font-weight: 500;
    font-size: var(--fs-sm);
    white-space: nowrap;
    transition: background-color 120ms var(--ease), border-color 120ms var(--ease), opacity 120ms;
    text-decoration: none;
  }
  .btn.sm {
    height: 30px;
    padding: 0 var(--sp-3);
    font-size: var(--fs-xs);
  }
  .btn:disabled,
  .btn[aria-disabled='true'] {
    opacity: 0.55;
    pointer-events: none;
  }
  .primary {
    background: var(--accent);
    color: var(--on-accent);
  }
  .primary:hover { background: var(--accent-hover); }
  .secondary {
    background: var(--raised);
    border-color: var(--border-strong);
    color: var(--text);
  }
  .secondary:hover { background: var(--overlay); }
  .ghost {
    background: transparent;
    color: var(--text-muted);
  }
  .ghost:hover {
    background: var(--hover);
    color: var(--text);
  }
  .danger {
    background: var(--danger-soft);
    color: var(--danger);
    border-color: transparent;
  }
  .danger:hover { background: var(--danger); color: #fff; }
  a.btn:hover { text-decoration: none; }
</style>
