export type Theme = 'dark' | 'light' | 'system';

const state = $state<{ current: Theme }>({ current: 'system' });

export function applyTheme(theme: Theme): void {
  state.current = theme;
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  if (theme === 'system') delete root.dataset.theme;
  else root.dataset.theme = theme;
}

export const theme = {
  get current() {
    return state.current;
  },
};
