<script lang="ts">
  import type { Snippet } from 'svelte';
  import Button from './Button.svelte';

  let {
    open = $bindable(false),
    title,
    confirmLabel = 'Confirm',
    cancelLabel = 'Cancel',
    danger = false,
    busy = false,
    onconfirm,
    oncancel,
    children,
  }: {
    open?: boolean;
    title: string;
    confirmLabel?: string;
    cancelLabel?: string;
    danger?: boolean;
    busy?: boolean;
    onconfirm?: () => void | Promise<void>;
    oncancel?: () => void;
    children: Snippet;
  } = $props();

  let el: HTMLDialogElement;

  $effect(() => {
    if (!el) return;
    if (open && !el.open) el.showModal();
    else if (!open && el.open) el.close();
  });

  function cancel() {
    open = false;
    oncancel?.();
  }
</script>

<dialog bind:this={el} onclose={cancel} onclick={(e) => e.target === el && cancel()}>
  <div class="panel" role="document">
    <h3>{title}</h3>
    <div class="content">{@render children()}</div>
    <footer>
      <Button variant="ghost" onclick={cancel} disabled={busy}>{cancelLabel}</Button>
      <Button variant={danger ? 'danger' : 'primary'} onclick={() => onconfirm?.()} loading={busy}>
        {confirmLabel}
      </Button>
    </footer>
  </div>
</dialog>

<style>
  dialog {
    border: 0;
    padding: 0;
    background: transparent;
    max-width: min(92vw, 460px);
    width: 100%;
  }
  dialog::backdrop {
    background: rgba(0, 0, 0, 0.55);
    backdrop-filter: blur(2px);
  }
  .panel {
    background: var(--overlay);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    padding: var(--sp-5);
    display: grid;
    gap: var(--sp-4);
    color: var(--text);
  }
  .content { color: var(--text-muted); font-size: var(--fs-sm); }
  footer { display: flex; justify-content: flex-end; gap: var(--sp-2); }
</style>
