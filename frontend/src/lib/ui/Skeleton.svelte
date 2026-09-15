<script lang="ts">
  let { width = '100%', height = '16px', radius = '6px' }: { width?: string; height?: string; radius?: string } = $props();
</script>

<span class="sk" style="width:{width};height:{height};border-radius:{radius}"></span>

<style>
  .sk {
    display: block;
    background: linear-gradient(90deg, var(--raised) 25%, var(--overlay) 50%, var(--raised) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.4s infinite;
  }
  @keyframes shimmer {
    from { background-position: 200% 0; }
    to { background-position: -200% 0; }
  }
</style>
