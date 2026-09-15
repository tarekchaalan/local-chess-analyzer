import { api } from '$lib/api/client';
import type { Settings } from '$lib/types/api';
import { applyTheme, type Theme } from './theme.svelte';

const state = $state<{ data: Settings; loaded: boolean }>({ data: {}, loaded: false });

async function load(): Promise<Settings> {
  state.data = await api.settings();
  state.loaded = true;
  applyTheme((state.data.theme as Theme) ?? 'system');
  return state.data;
}

async function update(values: Record<string, string | number | boolean>): Promise<string[]> {
  const res = await api.updateSettings(values);
  state.data = res.settings;
  if (res.updated.includes('theme')) applyTheme(state.data.theme as Theme);
  return res.updated;
}

export const settings = {
  get data() {
    return state.data;
  },
  get loaded() {
    return state.loaded;
  },
  get(key: string, fallback = ''): string {
    return state.data[key] ?? fallback;
  },
  bool(key: string): boolean {
    return state.data[key] === 'true';
  },
  int(key: string, fallback = 0): number {
    const n = Number.parseInt(state.data[key] ?? '', 10);
    return Number.isFinite(n) ? n : fallback;
  },
  load,
  update,
};
