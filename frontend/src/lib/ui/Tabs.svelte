<script lang="ts">
  let {
    value = $bindable(''),
    options,
    size = 'md',
    onchange,
  }: {
    value?: string;
    options: { value: string; label: string }[];
    size?: 'sm' | 'md';
    onchange?: (v: string) => void;
  } = $props();
</script>

<div class="tabs {size}" role="tablist">
  {#each options as o (o.value)}
    <button
      role="tab"
      aria-selected={value === o.value}
      class:active={value === o.value}
      onclick={() => {
        value = o.value;
        onchange?.(o.value);
      }}
    >
      {o.label}
    </button>
  {/each}
</div>

<style>
  .tabs {
    display: inline-flex;
    padding: 3px;
    gap: 2px;
    background: var(--raised);
    border: 1px solid var(--border);
    border-radius: var(--radius);
  }
  button {
    padding: 0 12px;
    height: 28px;
    border-radius: 4px;
    font-size: var(--fs-sm);
    color: var(--text-muted);
    font-weight: 500;
  }
  .sm button { height: 24px; font-size: var(--fs-xs); padding: 0 10px; }
  button:hover { color: var(--text); }
  button.active { background: var(--overlay); color: var(--text); box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3); }
</style>
