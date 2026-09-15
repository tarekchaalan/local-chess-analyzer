import type { GameEvent } from '$lib/api/sse';
import type { AnalysisStatus, GameListItem } from '$lib/types/api';

/** Live analysis_status overrides pushed over SSE, keyed by game id. */
const state = $state<{ byId: Record<number, AnalysisStatus> }>({ byId: {} });

export const gameStatus = {
  applyEvent(ev: GameEvent): void {
    state.byId = { ...state.byId, [ev.id]: ev.analysis_status as AnalysisStatus };
  },
  /** The freshest status we know for a game: a live event beats the value the list was loaded with. */
  of(game: Pick<GameListItem, 'id' | 'analysis_status'>): AnalysisStatus {
    return state.byId[game.id] ?? game.analysis_status;
  },
};
