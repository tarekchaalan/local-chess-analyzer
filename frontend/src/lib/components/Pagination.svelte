<script lang="ts">
  import Button from '$lib/ui/Button.svelte';
  import Icon from '$lib/ui/Icon.svelte';

  let { page, pageSize, total, onchange }: { page: number; pageSize: number; total: number; onchange: (p: number) => void } = $props();

  const pages = $derived(Math.max(1, Math.ceil(total / pageSize)));
  const from = $derived(total === 0 ? 0 : (page - 1) * pageSize + 1);
  const to = $derived(Math.min(total, page * pageSize));
</script>

<div class="pager">
  <span class="muted mono">{from.toLocaleString()}–{to.toLocaleString()} of {total.toLocaleString()}</span>
  <div class="btns">
    <Button size="sm" variant="ghost" disabled={page <= 1} onclick={() => onchange(1)} title="First"><Icon name="first" size={14} /></Button>
    <Button size="sm" variant="ghost" disabled={page <= 1} onclick={() => onchange(page - 1)} title="Previous"><Icon name="chevron-left" size={14} /></Button>
    <span class="mono page">{page} / {pages}</span>
    <Button size="sm" variant="ghost" disabled={page >= pages} onclick={() => onchange(page + 1)} title="Next"><Icon name="chevron-right" size={14} /></Button>
    <Button size="sm" variant="ghost" disabled={page >= pages} onclick={() => onchange(pages)} title="Last"><Icon name="last" size={14} /></Button>
  </div>
</div>

<style>
  .pager { display: flex; justify-content: space-between; align-items: center; gap: var(--sp-3); font-size: var(--fs-xs); flex-wrap: wrap; }
  .btns { display: flex; align-items: center; gap: 2px; }
  .page { padding: 0 8px; color: var(--text-muted); }
</style>
