<script lang="ts">
  import { toasts } from '$lib/stores/toasts.svelte';
  import Icon from './Icon.svelte';
</script>

<div class="toasts" aria-live="polite">
  {#each toasts.items as t (t.id)}
    <div class="toast {t.kind}" role="status">
      <span class="dot"></span>
      <span class="msg">{t.message}</span>
      <button class="close" onclick={() => toasts.dismiss(t.id)} aria-label="Dismiss"><Icon name="x" size={14} /></button>
    </div>
  {/each}
</div>

<style>
  .toasts {
    position: fixed;
    top: calc(var(--sp-4) + env(safe-area-inset-top, 0px));
    right: var(--sp-4);
    display: grid;
    gap: var(--sp-2);
    z-index: 100;
    max-width: min(92vw, 380px);
  }
  .toast {
    display: flex;
    align-items: center;
    gap: var(--sp-3);
    padding: 10px 12px;
    background: var(--overlay);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    font-size: var(--fs-sm);
    animation: in 160ms var(--ease);
  }
  .dot { width: 8px; height: 8px; border-radius: 50%; flex: none; background: var(--info); }
  .success .dot { background: var(--accent); }
  .error .dot { background: var(--danger); }
  .msg { flex: 1; }
  .close { color: var(--text-muted); display: inline-flex; }
  @keyframes in {
    from { opacity: 0; transform: translateY(-6px); }
    to { opacity: 1; transform: none; }
  }
</style>
