import type { Classification } from '$lib/types/api';

export interface ClassificationMeta {
  label: string;
  short: string;
  color: string; // CSS var
  symbol: string;
  description: string;
}

export const CLASSIFICATIONS: Record<Classification, ClassificationMeta> = {
  brilliant: { label: 'Brilliant', short: '!!', color: 'var(--c-brilliant)', symbol: '!!', description: 'A strong sacrifice the engine approves of' },
  great: { label: 'Great', short: '!', color: 'var(--c-great)', symbol: '!', description: 'The only good move in the position' },
  best: { label: 'Best', short: '★', color: 'var(--c-best)', symbol: '★', description: "The engine's top choice" },
  excellent: { label: 'Excellent', short: '✓', color: 'var(--c-excellent)', symbol: '✓', description: 'Nearly as good as the best move' },
  good: { label: 'Good', short: '✓', color: 'var(--c-good)', symbol: '✓', description: 'A solid move' },
  book: { label: 'Book', short: '📖', color: 'var(--c-book)', symbol: '▤', description: 'Known opening theory' },
  forced: { label: 'Forced', short: '→', color: 'var(--c-forced)', symbol: '→', description: 'The only legal move' },
  inaccuracy: { label: 'Inaccuracy', short: '?!', color: 'var(--c-inaccuracy)', symbol: '?!', description: 'A slightly weaker move' },
  mistake: { label: 'Mistake', short: '?', color: 'var(--c-mistake)', symbol: '?', description: 'Gives away a real part of the advantage' },
  miss: { label: 'Miss', short: '✕', color: 'var(--c-miss)', symbol: '✕', description: 'A missed opportunity' },
  blunder: { label: 'Blunder', short: '??', color: 'var(--c-blunder)', symbol: '??', description: 'A serious error' },
};

/** Display order for report cards (chess.com order). */
export const REPORT_ORDER: Classification[] = [
  'brilliant',
  'great',
  'best',
  'excellent',
  'good',
  'book',
  'inaccuracy',
  'mistake',
  'miss',
  'blunder',
];

/** Classifications worth marking on the eval graph. */
export const NOTABLE: Classification[] = ['brilliant', 'great', 'inaccuracy', 'mistake', 'miss', 'blunder'];

export function isBad(c: Classification): boolean {
  return c === 'inaccuracy' || c === 'mistake' || c === 'miss' || c === 'blunder';
}

export function sentence(san: string, c: Classification): string {
  switch (c) {
    case 'book':
      return `${san} is a book move`;
    case 'forced':
      return `${san} was forced`;
    case 'brilliant':
      return `${san} is brilliant`;
    case 'great':
      return `${san} is a great move`;
    case 'best':
      return `${san} is best`;
    case 'excellent':
      return `${san} is excellent`;
    case 'good':
      return `${san} is good`;
    case 'inaccuracy':
      return `${san} is an inaccuracy`;
    case 'mistake':
      return `${san} is a mistake`;
    case 'miss':
      return `${san} missed an opportunity`;
    case 'blunder':
      return `${san} is a blunder`;
  }
}
