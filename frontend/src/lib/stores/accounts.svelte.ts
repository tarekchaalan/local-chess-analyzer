import { api } from '$lib/api/client';
import type { AccountEvent } from '$lib/api/sse';
import type { Account, Platform } from '$lib/types/api';

const state = $state<{ list: Account[]; loaded: boolean }>({ list: [], loaded: false });

async function load(): Promise<Account[]> {
  state.list = await api.accounts();
  state.loaded = true;
  return state.list;
}

async function add(platform: Platform, username: string): Promise<Account> {
  const account = await api.createAccount(platform, username);
  state.list = [...state.list, account];
  return account;
}

async function remove(id: number): Promise<void> {
  await api.deleteAccount(id);
  state.list = state.list.filter((a) => a.id !== id);
}

function applyEvent(ev: AccountEvent): void {
  state.list = state.list.map((a) =>
    a.id === ev.id ? { ...a, game_count: ev.game_count, last_synced_at: ev.last_synced_at } : a,
  );
}

export const accounts = {
  get list() {
    return state.list;
  },
  get loaded() {
    return state.loaded;
  },
  byId(id: number | null | undefined): Account | undefined {
    return state.list.find((a) => a.id === id);
  },
  load,
  refresh: load,
  add,
  remove,
  applyEvent,
};
