<script lang="ts">
  let { label, value, hint, tone = 'neutral' }: { label: string; value: string; hint?: string; tone?: 'neutral' | 'success' | 'danger' | 'warning' } = $props();
</script>

<div class="tile">
  <span class="label">{label}</span>
  <span class="value mono {tone}">{value}</span>
  {#if hint}<span class="hint">{hint}</span>{/if}
</div>

<style>
  .tile {
    display: grid;
    gap: 2px;
    padding: var(--sp-4);
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    min-width: 0;
  }
  .label { font-size: var(--fs-xs); color: var(--text-muted); font-weight: 500; }
  .value { font-size: var(--fs-2xl); font-weight: 700; letter-spacing: -0.02em; line-height: 1.1; }
  .value.success { color: var(--accent); }
  .value.danger { color: var(--danger); }
  .value.warning { color: var(--warning); }
  .hint { font-size: var(--fs-xs); color: var(--text-faint); }
</style>
