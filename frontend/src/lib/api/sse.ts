import type { Job } from '$lib/types/api';

export interface GameEvent {
  id: number;
  analysis_status: string;
}
export interface AccountEvent {
  id: number;
  game_count: number;
  last_synced_at: string | null;
}

export interface SseHandlers {
  job?: (job: Job) => void;
  game?: (ev: GameEvent) => void;
  account?: (ev: AccountEvent) => void;
  open?: () => void;
  close?: () => void;
}

/** Connects to /api/events and reconnects with backoff. Returns a disconnect function. */
export function connectEvents(handlers: SseHandlers): () => void {
  let source: EventSource | null = null;
  let closed = false;
  let attempt = 0;
  let timer: ReturnType<typeof setTimeout> | null = null;

  const open = () => {
    if (closed) return;
    source = new EventSource('/api/events');
    source.addEventListener('ready', () => {
      attempt = 0;
      handlers.open?.();
    });
    source.addEventListener('job', (e) => handlers.job?.(JSON.parse((e as MessageEvent).data)));
    source.addEventListener('game', (e) => handlers.game?.(JSON.parse((e as MessageEvent).data)));
    source.addEventListener('account', (e) => handlers.account?.(JSON.parse((e as MessageEvent).data)));
    source.onerror = () => {
      source?.close();
      source = null;
      handlers.close?.();
      if (closed) return;
      const delay = Math.min(15000, 500 * 2 ** attempt++);
      timer = setTimeout(open, delay);
    };
  };

  open();
  return () => {
    closed = true;
    if (timer) clearTimeout(timer);
    source?.close();
    source = null;
  };
}
