export type ToastKind = 'success' | 'error' | 'info';
export interface Toast {
  id: number;
  kind: ToastKind;
  message: string;
}

const state = $state<{ items: Toast[] }>({ items: [] });
let nextId = 1;

function push(kind: ToastKind, message: string, ttl = 4000): void {
  const id = nextId++;
  state.items = [...state.items, { id, kind, message }];
  if (ttl > 0) setTimeout(() => dismiss(id), ttl);
}

function dismiss(id: number): void {
  state.items = state.items.filter((t) => t.id !== id);
}

export const toasts = {
  get items() {
    return state.items;
  },
  push,
  dismiss,
  success: (m: string) => push('success', m),
  error: (m: string) => push('error', m, 6000),
  info: (m: string) => push('info', m),
};
