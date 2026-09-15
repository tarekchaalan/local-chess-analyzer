import captureUrl from '$lib/sounds/capture.wav';
import castleUrl from '$lib/sounds/castle.wav';
import checkUrl from '$lib/sounds/move-check.wav';
import opponentUrl from '$lib/sounds/move-opponent.wav';
import selfUrl from '$lib/sounds/move-self.wav';
import promoteUrl from '$lib/sounds/promote.wav';
import type { ReplayMove } from './replay';

export type SoundName = 'move-self' | 'move-opponent' | 'capture' | 'castle' | 'move-check' | 'promote';

const URLS: Record<SoundName, string> = {
  'move-self': selfUrl,
  'move-opponent': opponentUrl,
  capture: captureUrl,
  castle: castleUrl,
  'move-check': checkUrl,
  promote: promoteUrl,
};

/** Which sound a move makes. Priority mirrors chess.com: check > promote > castle > capture > move. */
export function soundFor(move: ReplayMove, isUserMove: boolean): SoundName {
  if (move.check) return 'move-check';
  if (move.san.includes('=')) return 'promote';
  if (move.san.startsWith('O-O')) return 'castle';
  if (move.captured || move.san.includes('x')) return 'capture';
  return isUserMove ? 'move-self' : 'move-opponent';
}

const cache = new Map<SoundName, HTMLAudioElement>();

function element(name: SoundName): HTMLAudioElement | null {
  if (typeof Audio === 'undefined') return null;
  let el = cache.get(name);
  if (!el) {
    el = new Audio(URLS[name]);
    el.preload = 'auto';
    cache.set(name, el);
  }
  return el;
}

/** Warm the cache so the first move isn't late. Safe to call repeatedly. */
export function preloadSounds(): void {
  (Object.keys(URLS) as SoundName[]).forEach(element);
}

/** Play a sound; overlapping plays restart it. Autoplay refusals are swallowed. */
export function playSound(name: SoundName, volume = 0.8): void {
  const el = element(name);
  if (!el) return;
  try {
    el.volume = volume;
    el.currentTime = 0;
    void el.play().catch(() => {});
  } catch {
    /* no audio device / not allowed yet */
  }
}
