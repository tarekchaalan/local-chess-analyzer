<script lang="ts">
  import Button from '$lib/ui/Button.svelte';
  import Icon from '$lib/ui/Icon.svelte';

  let {
    ply,
    total,
    onseek,
    onflip,
  }: { ply: number; total: number; onseek: (ply: number) => void; onflip: () => void } = $props();
</script>

<div class="nav">
  <Button variant="ghost" size="sm" disabled={ply <= 0} onclick={() => onseek(0)} title="Start (Home)"><Icon name="first" size={16} /></Button>
  <Button variant="ghost" size="sm" disabled={ply <= 0} onclick={() => onseek(ply - 1)} title="Previous (←)"><Icon name="chevron-left" size={16} /></Button>
  <span class="mono pos">{ply} / {total}</span>
  <Button variant="ghost" size="sm" disabled={ply >= total} onclick={() => onseek(ply + 1)} title="Next (→)"><Icon name="chevron-right" size={16} /></Button>
  <Button variant="ghost" size="sm" disabled={ply >= total} onclick={() => onseek(total)} title="End (End)"><Icon name="last" size={16} /></Button>
  <span class="gap"></span>
  <Button variant="ghost" size="sm" onclick={onflip} title="Flip board (F)"><Icon name="flip" size={16} /></Button>
</div>

<style>
  .nav { display: flex; align-items: center; gap: 2px; }
  .pos { font-size: var(--fs-xs); color: var(--text-muted); padding: 0 8px; min-width: 64px; text-align: center; }
  .gap { flex: 1; }
</style>
