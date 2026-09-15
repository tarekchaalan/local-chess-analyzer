<script lang="ts">
  import type { Snippet } from 'svelte';
  type Tone = 'neutral' | 'success' | 'danger' | 'info' | 'warning' | 'accent';
  let { tone = 'neutral', class: cls = '', children }: { tone?: Tone; class?: string; children: Snippet } = $props();
</script>

<span class="badge {tone} {cls}">{@render children()}</span>

<style>
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 1px 8px;
    border-radius: 999px;
    font-size: var(--fs-xs);
    font-weight: 500;
    line-height: 18px;
    white-space: nowrap;
    background: var(--raised);
    color: var(--text-muted);
    border: 1px solid var(--border);
  }
  .success { background: var(--accent-soft); color: var(--accent); border-color: transparent; }
  .danger { background: var(--danger-soft); color: var(--danger); border-color: transparent; }
  .info { background: var(--info-soft); color: var(--info); border-color: transparent; }
  .warning { background: rgba(247, 198, 49, 0.14); color: var(--warning); border-color: transparent; }
  .accent { background: var(--accent); color: var(--on-accent); border-color: transparent; }
</style>
