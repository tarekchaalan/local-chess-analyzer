<script lang="ts">
  let {
    value = $bindable(''),
    options,
    label,
    id,
    disabled = false,
    size = 'md',
    onchange,
  }: {
    value?: string;
    options: { value: string; label: string }[];
    label?: string;
    id?: string;
    disabled?: boolean;
    size?: 'sm' | 'md';
    onchange?: (value: string) => void;
  } = $props();

  const fallbackId = `sel-${Math.random().toString(36).slice(2, 8)}`;
  const uid = $derived(id ?? fallbackId);
</script>

<label class="field {size}" for={uid}>
  {#if label}<span class="label">{label}</span>{/if}
  <span class="wrap">
    <select id={uid} bind:value {disabled} onchange={() => onchange?.(value)}>
      {#each options as o (o.value)}
        <option value={o.value}>{o.label}</option>
      {/each}
    </select>
  </span>
</label>

<style>
  .field { display: inline-flex; flex-direction: column; gap: 4px; min-width: 0; }
  .label { font-size: var(--fs-xs); color: var(--text-muted); font-weight: 500; }
  .wrap { position: relative; display: block; }
  .wrap::after {
    content: '';
    position: absolute;
    right: 10px;
    top: 50%;
    width: 6px;
    height: 6px;
    border-right: 1.5px solid var(--text-muted);
    border-bottom: 1.5px solid var(--text-muted);
    transform: translateY(-70%) rotate(45deg);
    pointer-events: none;
  }
  select {
    appearance: none;
    width: 100%;
    height: 36px;
    padding: 0 28px 0 10px;
    border-radius: var(--radius);
    border: 1px solid var(--border-strong);
    background: var(--raised);
    color: var(--text);
    font-size: var(--fs-sm);
  }
  .sm select { height: 30px; font-size: var(--fs-xs); }
  select:disabled { opacity: 0.55; }
</style>
