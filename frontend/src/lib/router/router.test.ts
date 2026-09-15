import { describe, expect, it } from 'vitest';
import { isActive, matchRoute, navigate, router } from './routing.svelte';

const Dummy = (() => {}) as any;

describe('matchRoute', () => {
  const routes = [
    { path: '/', component: Dummy },
    { path: '/games', component: Dummy },
    { path: '/games/:id', component: Dummy },
  ];

  it('matches static routes', () => {
    expect(matchRoute(routes, '/games')?.params).toEqual({});
    expect(matchRoute(routes, '/')?.params).toEqual({});
  });

  it('extracts params', () => {
    expect(matchRoute(routes, '/games/42')?.params).toEqual({ id: '42' });
    expect(matchRoute(routes, '/games/a%20b')?.params).toEqual({ id: 'a b' });
  });

  it('returns null for unknown paths', () => {
    expect(matchRoute(routes, '/nope')).toBeNull();
    expect(matchRoute(routes, '/games/1/2')).toBeNull();
  });

  it('ignores query strings', () => {
    expect(matchRoute(routes, '/games?x=1')?.params).toEqual({});
  });
});

describe('navigate', () => {
  it('updates location.hash and router state', () => {
    navigate('/settings');
    expect(location.hash).toBe('#/settings');
    expect(router.path).toBe('/settings');
    navigate('games/7');
    expect(router.path).toBe('/games/7');
  });
});

describe('isActive', () => {
  it('treats root specially', () => {
    expect(isActive('/', '/')).toBe(true);
    expect(isActive('/', '/games')).toBe(false);
    expect(isActive('/games', '/games/3')).toBe(true);
    expect(isActive('/games', '/gamesx')).toBe(false);
  });
});
