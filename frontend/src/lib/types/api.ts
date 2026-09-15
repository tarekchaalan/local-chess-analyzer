/** Mirrors backend/lca/api/schemas.py. */

export type Platform = 'chesscom' | 'lichess';
export type TimeClass = 'bullet' | 'blitz' | 'rapid' | 'classical' | 'daily';
export type UserResult = 'win' | 'loss' | 'draw';
export type Color = 'w' | 'b';
export type AnalysisStatus = 'none' | 'queued' | 'running' | 'done' | 'failed';
export type JobStatus = 'queued' | 'running' | 'done' | 'failed' | 'cancelled';
export type Classification =
  | 'book'
  | 'forced'
  | 'brilliant'
  | 'great'
  | 'best'
  | 'miss'
  | 'excellent'
  | 'good'
  | 'inaccuracy'
  | 'mistake'
  | 'blunder';

export interface Health {
  ok: boolean;
  version: string;
}

export interface Account {
  id: number;
  platform: Platform;
  username: string;
  created_at: string;
  last_synced_at: string | null;
  game_count: number;
  analyzed_count: number;
}

export interface Job {
  id: number;
  kind: 'analyze' | 'sync';
  game_id: number | null;
  account_id: number | null;
  params: Record<string, unknown> | null;
  status: JobStatus;
  progress: number;
  total: number;
  message: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export interface GameListItem {
  id: number;
  account_id: number;
  platform: Platform;
  platform_game_id: string;
  url: string | null;
  white: string;
  black: string;
  white_rating: number | null;
  black_rating: number | null;
  user_color: Color;
  result: string;
  user_result: UserResult;
  termination: string | null;
  time_class: TimeClass;
  time_control: string | null;
  rated: boolean;
  played_at: string;
  eco: string | null;
  opening_name: string | null;
  ply_count: number;
  analysis_status: AnalysisStatus;
  accuracy: number | null;
  opponent: string;
  opponent_rating: number | null;
  user_rating: number | null;
}

export interface Game extends GameListItem {
  pgn: string;
  platform_accuracy_white: number | null;
  platform_accuracy_black: number | null;
  imported_at: string;
}

export interface GameList {
  items: GameListItem[];
  total: number;
  page: number;
  page_size: number;
}

export type EvalJson = { cp: number } | { mate: number };

export interface EngineLineJson {
  uci: string;
  san: string;
  eval: EvalJson;
  line?: string[];
}

export interface MoveRecord {
  ply: number;
  san: string;
  uci: string;
  color: Color;
  eval_before: EvalJson;
  eval_after: EvalJson;
  best: EngineLineJson | null;
  second: EngineLineJson | null;
  win_before: number;
  win_after: number;
  accuracy: number;
  classification: Classification;
  book: boolean;
  clock: string | null;
}

export interface Analysis {
  game_id: number;
  engine_name: string;
  depth: number;
  time_ms: number;
  multipv: number;
  threads: number;
  hash_mb: number;
  created_at: string;
  accuracy_white: number;
  accuracy_black: number;
  opening_eco: string | null;
  opening_name: string | null;
  book_plies: number;
  counts: Record<Color, Record<Classification, number>>;
  moves: MoveRecord[];
}

export interface GameFilters {
  account_id?: number;
  platform?: Platform;
  time_class?: TimeClass;
  user_result?: UserResult;
  color?: Color;
  analysis_status?: AnalysisStatus;
  search?: string;
  date_from?: string;
  date_to?: string;
  sort?: 'played_at' | 'accuracy' | 'rating';
  order?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}

export interface ResultCounts {
  games: number;
  wins: number;
  draws: number;
  losses: number;
  win_rate: number | null;
}

export interface Overview extends ResultCounts {
  analyzed: number;
  mean_accuracy: number | null;
  accounts: number;
}

export interface TrendPoint {
  bucket: string;
  games: number;
  accuracy: number;
}

export interface TimeClassStat extends ResultCounts {
  time_class: TimeClass;
  analyzed: number;
  mean_accuracy: number | null;
  blunders_per_game: number | null;
  mistakes_per_game: number | null;
}

export interface OpeningStat extends ResultCounts {
  eco: string | null;
  name: string;
}

export interface ResultsByColor {
  white: ResultCounts;
  black: ResultCounts;
}

export type Settings = Record<string, string>;

export interface EngineInfo {
  path: string;
  exists: boolean;
  valid: boolean;
  name: string | null;
  message: string;
}

export interface SystemInfo {
  cpu: { physical_cores: number; logical_cores: number; usage_percent: number; recommended_threads: number };
  memory: { total_mb: number; available_mb: number; used_mb: number; usage_percent: number; recommended_hash_mb: number };
  engine: EngineInfo;
  recommended_depth: number;
  platform: string;
}

export interface ApiErrorBody {
  error: { code: string; message: string; details?: unknown };
}
