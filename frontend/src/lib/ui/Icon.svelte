<script lang="ts">
  export type IconName =
    | 'dashboard' | 'games' | 'accounts' | 'settings' | 'sync' | 'play' | 'x' | 'check'
    | 'chevron-left' | 'chevron-right' | 'first' | 'last' | 'search' | 'trash' | 'external'
    | 'menu' | 'plus' | 'warning' | 'flip' | 'download' | 'upload' | 'chesscom' | 'lichess'
    | 'info' | 'stop' | 'sparkle' | 'clock';

  let { name, size = 18, class: cls = '' }: { name: IconName; size?: number; class?: string } = $props();

  const paths: Record<IconName, string> = {
    dashboard: 'M3 3h8v8H3zM13 3h8v5h-8zM13 10h8v11h-8zM3 13h8v8H3z',
    games: 'M4 4h16v16H4zM4 9h16M4 14h16M9 4v16M14 4v16',
    accounts: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM4 21a8 8 0 0 1 16 0',
    settings: 'M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z',
    sync: 'M21 12a9 9 0 0 1-15.5 6.2L3 16M3 12a9 9 0 0 1 15.5-6.2L21 8M21 3v5h-5M3 21v-5h5',
    play: 'M6 4l14 8-14 8z',
    x: 'M6 6l12 12M18 6L6 18',
    check: 'M5 12l5 5L20 7',
    'chevron-left': 'M15 5l-7 7 7 7',
    'chevron-right': 'M9 5l7 7-7 7',
    first: 'M18 5l-7 7 7 7M8 5v14',
    last: 'M6 5l7 7-7 7M16 5v14',
    search: 'M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM20 20l-4-4',
    trash: 'M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3',
    external: 'M14 4h6v6M20 4l-9 9M19 14v6H4V5h6',
    menu: 'M4 7h16M4 12h16M4 17h16',
    plus: 'M12 5v14M5 12h14',
    warning: 'M12 3l10 18H2zM12 10v5M12 18v.5',
    flip: 'M7 3L3 7l4 4M3 7h13a5 5 0 0 1 5 5M17 21l4-4-4-4M21 17H8a5 5 0 0 1-5-5',
    download: 'M12 4v12M6 10l6 6 6-6M4 20h16',
    upload: 'M12 16V4M6 10l6-6 6 6M4 20h16',
    chesscom: 'M8 20h8M9 17h6l-1-4h1a4 4 0 0 0 0-8h-1l1-2H9l1 2H9a4 4 0 0 0 0 8h1z',
    lichess: 'M8 21h8M10 18l-1-6 4-8 3 3-2 4h3l-3 7z',
    info: 'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM12 8v.5M12 11v6',
    stop: 'M6 6h12v12H6z',
    sparkle: 'M12 2l2 6 6 2-6 2-2 6-2-6-6-2 6-2zM19 15l1 3 3 1-3 1-1 3-1-3-3-1 3-1z',
    clock: 'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM12 7v5l3 3',
  };
</script>

<svg
  class={cls}
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="1.8"
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden="true"
>
  <path d={paths[name]} />
</svg>
