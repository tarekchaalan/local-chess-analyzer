import type {
  Account,
  Analysis,
  ApiErrorBody,
  EngineInfo,
  Game,
  GameFilters,
  GameList,
  Health,
  Job,
  OpeningStat,
  Overview,
  Platform,
  ResultsByColor,
  Settings,
  SystemInfo,
  TimeClassStat,
  TrendPoint,
} from '$lib/types/api';

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: unknown,
  ) {
    super(message);
  }
}

const BASE = '/api';

async function request<T>(method: string, path: string, body?: unknown, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {};
  let payload: BodyInit | undefined;
  if (body instanceof FormData) payload = body;
  else if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
    payload = JSON.stringify(body);
  }
  let res: Response;
  try {
    res = await fetch(BASE + path, { method, headers, body: payload, ...init });
  } catch (e) {
    throw new ApiError(0, 'network_error', 'Could not reach the server');
  }
  if (res.status === 204) return undefined as T;
  const text = await res.text();
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }
  if (!res.ok) {
    const err = (data as ApiErrorBody | null)?.error;
    throw new ApiError(res.status, err?.code ?? 'http_error', err?.message ?? res.statusText, err?.details);
  }
  return data as T;
}

function qs(params: Record<string, unknown>): string {
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === '') continue;
    sp.set(k, String(v));
  }
  const s = sp.toString();
  return s ? `?${s}` : '';
}

export const api = {
  health: () => request<Health>('GET', '/health'),

  // accounts
  accounts: () => request<Account[]>('GET', '/accounts'),
  createAccount: (platform: Platform, username: string) =>
    request<Account>('POST', '/accounts', { platform, username }),
  deleteAccount: (id: number) => request<void>('DELETE', `/accounts/${id}`),
  syncAccount: (id: number, months?: number | null) =>
    request<Job>('POST', `/accounts/${id}/sync`, months ? { months } : {}),
  syncAll: () => request<Job[]>('POST', '/accounts/sync-all'),

  // games
  games: (filters: GameFilters = {}) => request<GameList>('GET', `/games${qs({ ...filters })}`),
  game: (id: number) => request<Game>('GET', `/games/${id}`),
  analysis: (id: number) => request<Analysis>('GET', `/games/${id}/analysis`),
  analyze: (id: number, force = false) => request<Job>('POST', `/games/${id}/analyze`, { force }),
  bulkAnalyze: (game_ids: number[], force = false) =>
    request<{ jobs: Job[]; skipped: number[] }>('POST', '/games/analyze', { game_ids, force }),
  deleteAnalysis: (id: number) => request<void>('DELETE', `/games/${id}/analysis`),

  // jobs
  jobs: (status?: string) => request<Job[]>('GET', `/jobs${qs({ status })}`),
  job: (id: number) => request<Job>('GET', `/jobs/${id}`),
  cancelJob: (id: number) => request<Job>('POST', `/jobs/${id}/cancel`),
  cancelAllJobs: () => request<{ count: number }>('POST', '/jobs/cancel-all'),
  clearFinishedJobs: () => request<{ count: number }>('DELETE', '/jobs/finished'),

  // stats
  overview: (account_id?: number) => request<Overview>('GET', `/stats/overview${qs({ account_id })}`),
  accuracyTrend: (bucket: 'week' | 'month', account_id?: number) =>
    request<TrendPoint[]>('GET', `/stats/accuracy-trend${qs({ bucket, account_id })}`),
  byTimeClass: (account_id?: number) =>
    request<TimeClassStat[]>('GET', `/stats/by-time-class${qs({ account_id })}`),
  openings: (account_id?: number, color?: 'w' | 'b', limit = 8) =>
    request<OpeningStat[]>('GET', `/stats/openings${qs({ account_id, color, limit })}`),
  results: (account_id?: number) => request<ResultsByColor>('GET', `/stats/results${qs({ account_id })}`),

  // settings / system
  settings: () => request<Settings>('GET', '/settings'),
  updateSettings: (values: Record<string, string | number | boolean>) =>
    request<{ updated: string[]; settings: Settings }>('PATCH', '/settings', values),
  system: () => request<SystemInfo>('GET', '/system'),
  validateEngine: (path: string) => request<EngineInfo>('POST', '/system/engine/validate', { path }),

  // database
  exportUrl: () => `${BASE}/database/export`,
  importDatabase: (file: File) => {
    const fd = new FormData();
    fd.append('file', file);
    return request<{ games: number; accounts: number; backup_path: string | null }>('POST', '/database/import', fd);
  },
  resetDatabase: () => request<{ deleted_games: number; deleted_accounts: number }>('POST', '/database/reset'),
};
