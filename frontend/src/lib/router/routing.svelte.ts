/** Minimal hash router: `#/games/42` -> path `/games/42`. */
import type { Component } from 'svelte';

export type RouteDef = { path: string; component: Component<any> };
export type RouteMatch = { component: Component<any>; params: Record<string, string> };

function readPath(): string {
  if (typeof location === 'undefined') return '/';
  const raw = location.hash.replace(/^#/, '') || '/';
  return raw.startsWith('/') ? raw : `/${raw}`;
}

export const router = $state({ path: readPath() });

if (typeof window !== 'undefined') {
  window.addEventListener('hashchange', () => {
    router.path = readPath();
  });
}

export function navigate(path: string): void {
  const target = path.startsWith('/') ? path : `/${path}`;
  if (typeof location !== 'undefined') location.hash = target;
  router.path = target;
}

export function matchRoute(routes: RouteDef[], path: string): RouteMatch | null {
  const [pathname] = path.split('?');
  const segs = pathname.split('/').filter(Boolean);
  for (const route of routes) {
    const rsegs = route.path.split('/').filter(Boolean);
    if (rsegs.length !== segs.length) continue;
    const params: Record<string, string> = {};
    let ok = true;
    for (let i = 0; i < rsegs.length; i++) {
      const r = rsegs[i];
      if (r.startsWith(':')) params[r.slice(1)] = decodeURIComponent(segs[i]);
      else if (r !== segs[i]) {
        ok = false;
        break;
      }
    }
    if (ok) return { component: route.component, params };
  }
  return null;
}

export function isActive(path: string, current: string): boolean {
  if (path === '/') return current === '/';
  return current === path || current.startsWith(path + '/');
}
