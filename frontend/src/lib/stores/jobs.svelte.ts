import { api } from '$lib/api/client';
import type { Job } from '$lib/types/api';

const state = $state<{ list: Job[]; loaded: boolean }>({ list: [], loaded: false });

const ACTIVE = new Set(['queued', 'running']);

async function load(): Promise<void> {
  state.list = await api.jobs();
  state.loaded = true;
}

function applyEvent(job: Job): void {
  const idx = state.list.findIndex((j) => j.id === job.id);
  if (idx === -1) state.list = [job, ...state.list].slice(0, 300);
  else state.list = state.list.map((j) => (j.id === job.id ? job : j));
}

async function cancel(id: number): Promise<void> {
  const job = await api.cancelJob(id);
  applyEvent(job);
}

async function cancelAll(): Promise<number> {
  const { count } = await api.cancelAllJobs();
  await load();
  return count;
}

async function clearFinished(): Promise<number> {
  const { count } = await api.clearFinishedJobs();
  state.list = state.list.filter((j) => ACTIVE.has(j.status));
  return count;
}

export const jobs = {
  get list() {
    return state.list;
  },
  get loaded() {
    return state.loaded;
  },
  get active(): Job[] {
    return state.list.filter((j) => ACTIVE.has(j.status));
  },
  get running(): Job | undefined {
    return state.list.find((j) => j.status === 'running' && j.kind === 'analyze');
  },
  /** The newest job for a game, only if it is still active. */
  forGame(gameId: number): Job | undefined {
    const newest = state.list.filter((j) => j.kind === 'analyze' && j.game_id === gameId).sort((a, b) => b.id - a.id)[0];
    return newest && ACTIVE.has(newest.status) ? newest : undefined;
  },
  forAccount(accountId: number): Job | undefined {
    const newest = state.list.filter((j) => j.kind === 'sync' && j.account_id === accountId).sort((a, b) => b.id - a.id)[0];
    return newest && ACTIVE.has(newest.status) ? newest : undefined;
  },
  load,
  applyEvent,
  cancel,
  cancelAll,
  clearFinished,
};
