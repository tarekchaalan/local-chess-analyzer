<script lang="ts">
  let {
    value = $bindable(''),
    label,
    id,
    type = 'text',
    placeholder,
    disabled = false,
    hint,
    error,
    mono = false,
    size = 'md',
    min,
    max,
    oninput,
    onkeydown,
  }: {
    value?: string;
    label?: string;
    id?: string;
    type?: 'text' | 'number' | 'date' | 'password' | 'search';
    placeholder?: string;
    disabled?: boolean;
    hint?: string;
    error?: string | null;
    mono?: boolean;
    size?: 'sm' | 'md';
    min?: number;
    max?: number;
    oninput?: (v: string) => void;
    onkeydown?: (e: KeyboardEvent) => void;
  } = $props();

  const fallbackId = `in-${Math.random().toString(36).slice(2, 8)}`;
  const uid = $derived(id ?? fallbackId);
</script>

<label class="field {size}" for={uid}>
  {#if label}<span class="label">{label}</span>{/if}
  <input
    id={uid}
    {type}
    bind:value
    {placeholder}
    {disabled}
    {min}
    {max}
    class:mono
    class:invalid={!!error}
    oninput={() => oninput?.(value)}
    {onkeydown}
  />
  {#if error}<span class="error">{error}</span>{:else if hint}<span class="hint">{hint}</span>{/if}
</label>

<style>
  .field { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
  .label { font-size: var(--fs-xs); color: var(--text-muted); font-weight: 500; }
  input {
    height: 36px;
    padding: 0 10px;
    border-radius: var(--radius);
    border: 1px solid var(--border-strong);
    background: var(--raised);
    color: var(--text);
    font-size: var(--fs-sm);
    width: 100%;
  }
  .sm input { height: 30px; font-size: var(--fs-xs); }
  input::placeholder { color: var(--text-faint); }
  input:disabled { opacity: 0.55; }
  input.invalid { border-color: var(--danger); }
  .hint { font-size: var(--fs-xs); color: var(--text-faint); }
  .error { font-size: var(--fs-xs); color: var(--danger); }
</style>
