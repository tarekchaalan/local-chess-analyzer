# Local Chess Analyzer v2 — Rewrite Design

**Date:** 2026-09-15
**Status:** Approved (user delegated remaining decisions)
**Scope:** Clean rewrite of backend and frontend in place. Fresh data schema (no migration). Multi-account across chess.com and Lichess. chess.com-standard move classification. Background job queue with live progress. Dark-first redesign.

---

## 1. Goals and non-goals

### Goals
- One local, offline-capable app that pulls a user's games from **chess.com and Lichess** (any number of accounts) into one library.
- **Game Review** parity with chess.com: per-move classifications (Brilliant → Blunder, plus Book, Forced, Miss), accuracy per player, opening name, evaluation graph, best-move lines.
- **Aggregate insights** across games: accuracy trend, results by colour, blunder rate by time class, most common openings.
- Analysis runs in a **background queue** with live progress; survives page reloads; cancellable.
- Codebase that is small-moduled, typed, and tested. Pure analysis logic has no I/O.
- Keep shipping as **PyInstaller desktop bundles** (mac/win/linux) and **Docker** images.

### Non-goals
- Migrating v1 databases or analysis files (users re-sync; games are re-downloadable).
- Playing against the engine, PGN import from disk, or any cloud features.
- Reproducing chess.com's proprietary CAPS2 accuracy exactly (see §5.5).

---

## 2. Architecture

Single FastAPI process (modular monolith). An `asyncio` job runner inside the process drives Stockfish via `python-chess`'s async UCI client and streams progress over Server-Sent Events. SQLite via SQLAlchemy 2.0 async. The Svelte 5 SPA is built to static files and served by FastAPI at `/`, so the PyInstaller bundle stays one executable and Docker stays two containers (nginx serves the SPA and proxies `/api`).

```
┌──────────────── FastAPI process ────────────────┐
│  api/ routers ──► services/ ──► db/ (SQLite)     │
│                     │                            │
│                 jobs.JobRunner                   │
│                 ├─ analysis lane ─► EngineSession │──► stockfish (UCI)
│                 └─ sync lane ─────► platforms/    │──► api.chess.com / lichess.org
│                     │                            │
│                 EventBus ──► GET /api/events (SSE)│
│  StaticFiles("/") ──► frontend/dist              │
└──────────────────────────────────────────────────┘
```

Why in-process rather than a separate worker: a single-user local app gains nothing from parallel games (Stockfish scales with threads on one game), and one process is what PyInstaller bundles cleanly.

---

## 3. Repository layout

```
backend/
  pyproject.toml            uv-managed; deps, ruff, pytest config
  lca/
    __init__.py
    main.py                 create_app(); lifespan: init DB, start JobRunner, mount SPA
    cli.py                  desktop entrypoint: open browser, run uvicorn (PyInstaller target)
    config.py               paths (dev vs bundled), defaults, engine binary resolution
    db/
      engine.py             async engine + session factory (echo off)
      models.py             SQLAlchemy 2.0 typed models
      bootstrap.py          create_all + defaults seeding + crash recovery (running→queued)
    domain/                 PURE: no I/O, no DB, no engine process
      winprob.py            cp/mate → win%
      classify.py           chess.com-standard classifier
      sacrifice.py          static exchange evaluation, en-prise detection
      accuracy.py           per-move + per-game accuracy
      openings.py           ECO book lookup (bundled JSON)
      pgn.py                header parsing, clock extraction, time-class normalization
      types.py              dataclasses: EngineLine, PositionEval, MoveRecord, Report
    platforms/
      base.py               Platform protocol, NormalizedGame, PlatformError
      chesscom.py
      lichess.py
    services/
      engine.py             EngineSession: lifecycle, options, analyse(board, multipv)
      analysis.py           analyze_game(pgn, ...) → Report  (engine + domain)
      sync.py               sync_account(account, ...) → counts
      jobs.py               JobRunner, lanes, EventBus, cancellation
      stats.py              aggregate queries
      system.py             cpu/memory info, engine validation, recommendations
      settings.py           typed settings accessor with defaults
    api/
      deps.py               get_session, get_runner, get_bus
      schemas.py            pydantic models for every response
      errors.py             exception handlers → {error:{code,message}}
      accounts.py games.py jobs.py stats.py settings.py system.py database.py events.py
    data/
      openings.json         epd → {eco, name} (generated from lichess/chess-openings, CC0)
  scripts/
    build_openings.py       regenerates data/openings.json from the upstream TSVs
  tests/
    domain/  platforms/  api/  fixtures/

frontend/
  package.json  vite.config.ts  svelte.config.js  tsconfig.json
  index.html
  src/
    main.ts  App.svelte
    lib/
      router/               hash router: routes table, params, navigate(), <Link>
      api/                  client.ts (typed fetch), sse.ts
      stores/               *.svelte.ts runes stores: accounts, settings, jobs, theme, toasts
      types/                api.ts (mirrors backend schemas)
      chess/                eval.ts, classification.ts, clocks.ts, replay.ts
      ui/                   Button Card Dialog Toast Select Tabs Badge EmptyState Skeleton Icon
      components/           Sidebar JobsTray Board EvalBar EvalGraph MoveList ReportCard
                            MoveDetail GameRow FilterBar Pagination StatTile charts/
      icons/classification/ inline SVG components, one per classification
    routes/                 Setup Dashboard Games GameReview Accounts Settings NotFound
    styles/                 tokens.css base.css
```

Import root for the backend is `lca` (run from `backend/`). The old `backend/app` package is deleted.

---

## 4. Data model (SQLite, file `data/lca.db`)

All timestamps UTC ISO-8601 strings. `id` columns are integer autoincrement.

### accounts
| column | type | notes |
|---|---|---|
| id | int PK | |
| platform | text | `chesscom` \| `lichess` |
| username | text | as entered / as returned by the platform |
| username_key | text | lowercased; **unique(platform, username_key)** |
| created_at | text | |
| last_synced_at | text? | |
| sync_cursor | text? | chess.com: last archive `YYYY/MM` fetched; Lichess: last `createdAt` ms |
| game_count | int | denormalized, updated after sync |

### games
| column | type | notes |
|---|---|---|
| id | int PK | |
| account_id | int FK→accounts (cascade delete) | |
| platform | text | |
| platform_game_id | text | chess.com `uuid`, Lichess `id`; **unique(platform, platform_game_id)** |
| url | text | |
| pgn | text | full PGN incl. clocks |
| white, black | text | usernames |
| white_rating, black_rating | int? | |
| user_color | text | `w` \| `b` — side the linked account played |
| result | text | `1-0` \| `0-1` \| `1/2-1/2` |
| user_result | text | `win` \| `loss` \| `draw` |
| termination | text? | human-readable (`resignation`, `timeout`, `checkmate`, …) |
| time_class | text | `bullet` \| `blitz` \| `rapid` \| `classical` \| `daily` |
| time_control | text? | raw (`600`, `180+2`, `1/86400`) |
| rated | bool | |
| played_at | text | UTC; indexed |
| eco, opening_name | text? | as provided by the platform (Lichess gives both; chess.com gives ECO + URL) |
| platform_accuracy_white, platform_accuracy_black | real? | chess.com only |
| ply_count | int | |
| imported_at | text | |
| analysis_status | text | `none` \| `queued` \| `running` \| `done` \| `failed`; indexed |

Indexes: `(account_id)`, `(played_at)`, `(time_class)`, `(analysis_status)`, `(user_result)`.

If the same game is imported through two linked accounts (user played themself), the first import wins; `user_color` reflects that account.

### analyses
| column | type | notes |
|---|---|---|
| game_id | int PK FK→games (cascade delete) | |
| engine_name | text | from UCI `id name` |
| depth, time_ms, multipv, threads, hash_mb | int | settings used |
| created_at | text | |
| accuracy_white, accuracy_black | real | our formula (§5.5) |
| opening_eco, opening_name, book_plies | text?, text?, int | from our book |
| counts | json | `{"w": {"brilliant": 0, …}, "b": {…}}` |
| moves | json | array of MoveRecord (§5.6) |

### jobs
| column | type | notes |
|---|---|---|
| id | int PK | |
| kind | text | `analyze` \| `sync` |
| game_id | int? FK→games (cascade) | for `analyze` |
| account_id | int? FK→accounts (cascade) | for `sync` |
| params | json? | e.g. `{"months": 3}` for sync |
| status | text | `queued` \| `running` \| `done` \| `failed` \| `cancelled` |
| progress, total | int | plies for analyze; games fetched / archives for sync |
| message | text? | current step or error |
| created_at, started_at, finished_at | text? | |

### settings
`key TEXT PK, value TEXT`. Keys and defaults live in `services/settings.py`:

| key | default | notes |
|---|---|---|
| engine_path | resolved bundled binary | |
| engine_threads | `max(1, logical_cores − 2)` | |
| engine_hash_mb | `clamp(available_mb × 0.15, 128, 2048)` | |
| analysis_depth | `18` | |
| analysis_time_ms | `2000` | 0 disables the time cap |
| auto_analyze_new_games | `false` | |
| theme | `system` | `dark` \| `light` \| `system` |
| lichess_token | `""` | optional, raises rate limit |
| setup_completed | `false` | |

---

## 5. Analysis pipeline

### 5.1 Engine session (`services/engine.py`)
- `chess.engine.popen_uci(engine_path)` (asyncio variant). One process kept alive across jobs; lazily started; restarted when engine settings change or on `EngineTerminatedError`.
- Options: `Threads`, `Hash`, `MultiPV = 2`.
- `analyse(board, limit)` returns two `EngineLine`s (`move`, `score` as `PovScore`, `pv[:8]`). `Limit(depth=analysis_depth, time=analysis_time_ms/1000 or None)` — whichever ends first.
- Position after the last move: if `board.is_game_over()` produce a terminal eval (mate 0 for checkmate, cp 0 otherwise); else run one `multipv=1` analyse.

### 5.2 Per-game flow (`services/analysis.py`)
1. Parse PGN with `chess.pgn`; extract clocks per ply (`[%clk …]`) via `domain/pgn.py`.
2. For each ply `i` (position `P_i` before move `m_i`): analyse `P_i` → PV1 (`best`), PV2 (`second`).
3. Eval **before** `m_i` = PV1 score at `P_i`. Eval **after** `m_i` = PV1 score at `P_{i+1}` (or terminal). Both normalized to White POV for storage, and to mover POV for classification.
4. Book tracking: walk `board.epd()` after each move against `openings.json`; once a position is not in the book, all subsequent moves are out of book.
5. Classify (§5.4), compute per-move accuracy (§5.5), report progress after every ply, check cancellation.
6. Aggregate counts, game accuracies, opening; persist `analyses` row; set `games.analysis_status = done`.

### 5.3 Win probability (`domain/winprob.py`)
From White-POV centipawns: `win = 50 + 50 · (2 / (1 + e^(−0.00368208·cp)) − 1)`, clamped to [0,100]. Mate for White → 100, mate for Black → 0. Mover POV: `100 − win` when mover is Black.

### 5.4 Classification (`domain/classify.py`) — chess.com standard
Inputs per move: `win_before`, `win_after` (mover POV), `best_move`, `second_win` (PV2 win, mover POV, may be None), `played_move`, boards before/after, `in_book`, `legal_move_count`, `prev_classification` (opponent's move), `best_is_mate`, `mover_mated_before`.
`Δ = win_before − win_after`.

Evaluated top-down; first match wins.

| # | Label | Rule |
|---|---|---|
| 1 | **Book** | `in_book` (position after the move is in the book and all prior moves were Book) |
| 2 | **Forced** | `legal_move_count == 1` |
| 3 | **Brilliant** | `Δ ≤ 2` **and** `is_piece_sacrifice(before, after, move)` (§5.4.1) **and** `win_after ≥ 40` **and** `win_before ≤ 90` **and** not `mover_mated_before` |
| 4 | **Great** | `played == best_move` **and** `second_win is not None` **and** `win_before − second_win ≥ 10` **and** `win_before ≥ 30` **and** not `is_simple_recapture(before, move)` |
| 5 | **Best** | `played == best_move` **or** `Δ ≤ 0` |
| 6 | **Miss** | (`prev_classification ∈ {Mistake, Blunder}` **or** `best_is_mate`) **and** `Δ ≥ 10` **and** `win_after ≥ 50` |
| 7 | **Excellent** | `Δ ≤ 2` |
| 8 | **Good** | `Δ ≤ 5` |
| 9 | **Inaccuracy** | `Δ ≤ 10` |
| 10 | **Mistake** | `Δ ≤ 20` |
| 11 | **Blunder** | otherwise |

Notes:
- Thresholds 2/5/10/20 are the widely reported chess.com expected-points thresholds (0.02/0.05/0.10/0.20). Because win% saturates, moves in decided positions are judged leniently, matching chess.com's eval-dependent behaviour.
- `is_simple_recapture`: the move is a capture whose destination is the square the opponent captured on with their previous move.

#### 5.4.1 Sacrifice detection (`domain/sacrifice.py`)
Piece values P=1, N=3, B=3, R=5, Q=9 (king ∞, never counted).
- `see(board, square, side)`: standard static exchange evaluation — iterate captures on `square` using least-valuable attacker first, alternating sides, with the swap-list / minimax back-propagation. Returns net material gained by `side` starting the exchange (≥ 0; a side never enters a losing exchange).
- `en_prise(board, square)`: piece on `square` belongs to `side_to_move`'s opponent and `see(board, square, side_to_move) > 0`.
- `is_piece_sacrifice(before, after, move)`:
  1. `captured = value of the piece captured by move` (0 if none; en passant → 1).
  2. `candidates = mover's pieces with value ≥ 3 on `after` that are en prise for the opponent`, restricted to pieces that were **not** en prise on `before` **or** the moved piece itself.
  3. `loss = max(see(after, sq, opponent) for sq in candidates, default 0)`.
  4. Sacrifice iff `loss − captured ≥ 2`.
  Examples: Bxh7+ Kxh7 → 3−1 = 2 ✓; Rxc3 bxc3 (exchange sac) → 5−3 = 2 ✓; Qxd8 Rxd8 → SEE 4 − 9 < 0 ✗; pawn sacs → 1 ✗; pieces already hanging before the move ✗.

### 5.5 Accuracy (`domain/accuracy.py`) — Lichess formula (public)
- Per move: `acc = clamp(103.1668 · e^(−0.04354·max(Δ,0)) − 3.1669, 0, 100)`.
- Per game per colour: let `w_k = clamp(stddev(win% over sliding window of ~ply_count/10, min 2, max 8 plies around move k), 0.5, 12)`; `weighted = Σ acc_k·w_k / Σ w_k`; `harmonic = n / Σ(1/acc_k)` (with 0 → tiny epsilon); `accuracy = (weighted + harmonic) / 2`.
- chess.com's own `accuracies` (when present in the API payload) are stored on the game and shown next to ours in the UI, labelled as chess.com's.

### 5.6 MoveRecord (stored in `analyses.moves`)
```json
{
  "ply": 12, "san": "Bxh7+", "uci": "d3h7", "color": "w",
  "eval_before": {"cp": 35}, "eval_after": {"cp": 210},          // White POV; or {"mate": 3}
  "best": {"uci": "d3h7", "san": "Bxh7+", "eval": {"cp": 210}, "line": ["Bxh7+","Kxh7","Ng5+","Kg8","Qh5"]},
  "second": {"uci": "c3e4", "san": "Ne4", "eval": {"cp": 40}},   // or null
  "win_before": 53.2, "win_after": 68.9,                          // mover POV
  "accuracy": 100.0,
  "classification": "brilliant",
  "book": false,
  "clock": "0:09:41.3"                                            // or null
}
```
FENs are not stored; the frontend replays SAN with chess.js.

### 5.7 Opening book (`domain/openings.py`, `data/openings.json`)
Generated by `scripts/build_openings.py` from the Lichess `chess-openings` TSVs (CC0): replay each entry's PGN, key by `board.epd()` → `{eco, name}`. ~3.5k entries, ~400 KB. Loaded once at startup into a dict. Game opening = the entry for the deepest Book ply.

---

## 6. Platforms and sync

### 6.1 Protocol (`platforms/base.py`)
```python
class NormalizedGame: platform, platform_game_id, url, pgn, white, black,
    white_rating, black_rating, result, termination, time_class, time_control,
    rated, played_at, eco, opening_name, platform_accuracy_white, platform_accuracy_black

class Platform(Protocol):
    name: str
    async def validate_user(self, username) -> str | None         # canonical username or None
    def fetch_games(self, username, cursor) -> AsyncIterator[tuple[NormalizedGame, str]]  # (game, new_cursor)
```
`PlatformError(code, message)` for HTTP/parse failures; 404 → `user_not_found`, 429 → `rate_limited`.

### 6.2 chess.com (`platforms/chesscom.py`) — verified against live API 2026-09-15
- `GET /pub/player/{u}/games/archives` → `archives[]`. Cursor = `YYYY/MM` of the last archive fetched; on incremental sync refetch from that month onward (games can land in an archive after it was last read). Optional `months` param limits to the most recent N archives.
- `GET {archive}` → `games[]`. Keep only `rules == "chess"` and `initial_setup` == standard start. ID = `uuid`. Fields used: `pgn`, `url`, `white/black.{username,rating,result}`, `end_time`, `time_class`, `time_control`, `rated`, `eco` (URL; ECO code from the PGN `[ECO]` header), `accuracies`.
- Result: `white.result == "win"` → `1-0`; `black.result == "win"` → `0-1`; else `1/2-1/2`. Termination from the losing/drawing side's result code (`checkmated`, `resigned`, `timeout`, `stalemate`, `repetition`, `agreed`, `insufficient`, `50move`, `timevsinsufficient`, `abandoned`).
- Requires a descriptive `User-Agent` (chess.com blocks generic ones).

### 6.3 Lichess (`platforms/lichess.py`) — verified against live API 2026-09-15
- `GET /api/games/user/{u}?since={cursor}&pgnInJson=true&clocks=true&opening=true&perfType=ultraBullet,bullet,blitz,rapid,classical,correspondence` with `Accept: application/x-ndjson`, streamed. Keep only `variant == "standard"`. ID = `id`.
- Fields: `pgn`, `players.{white,black}.{user.name, rating}`, `winner`, `status`, `speed`, `clock`, `rated`, `createdAt`, `opening.{eco,name}`.
- `speed` → `time_class`: `ultraBullet→bullet`, `bullet`, `blitz`, `rapid`, `classical`, `correspondence→daily`.
- Cursor = `max(createdAt) + 1`. Respect `429` + `Retry-After`. Optional `Authorization: Bearer` from settings.
- `GET /api/user/{u}` for validation.

### 6.4 Sync job (`services/sync.py`)
Streams games, upserts in batches of 100 with `INSERT … ON CONFLICT DO NOTHING`, computes `user_color`/`user_result`, updates progress (`archives fetched / total` for chess.com; `games fetched` for Lichess), stores the new cursor and `last_synced_at`, refreshes `game_count`. If `auto_analyze_new_games`, enqueues an `analyze` job per new game.

---

## 7. Jobs and events

### 7.1 JobRunner (`services/jobs.py`)
- Two lanes, each an `asyncio.Task` looping: pick the oldest `queued` job of its kind → mark `running` → execute → mark `done|failed|cancelled`.
- Lane `analysis` runs `analyze` jobs serially (Stockfish already uses all configured threads). Lane `sync` runs `sync` jobs serially. Lanes run concurrently with each other.
- Cancellation: `cancel(job_id)` sets a flag; queued jobs flip to `cancelled` immediately; running jobs are checked between plies / between batches (latency ≤ one engine call).
- Startup recovery: `running → queued`. Shutdown: cancel lanes, `engine.quit()`.
- Duplicate protection: enqueueing `analyze` for a game that already has a queued/running job returns the existing job.

### 7.2 EventBus and SSE (`api/events.py`)
In-memory fan-out; each SSE client gets an `asyncio.Queue` (bounded, drop-oldest). Events:
- `job` — `{id, kind, game_id, account_id, status, progress, total, message}`
- `game` — `{id, analysis_status}`
- `account` — `{id, game_count, last_synced_at}`
Keepalive comment every 15 s. Frontend reconnects with backoff and re-fetches jobs on reconnect.

---

## 8. HTTP API

All under `/api`. JSON. Pydantic response models in `api/schemas.py`. Errors: `{"error": {"code": "...", "message": "..."}}` with appropriate status (400 validation, 404 not found, 409 conflict, 422 platform, 502 upstream, 500).

| Method & path | Purpose |
|---|---|
| `GET /health` | `{ok, version}` |
| `GET /accounts` | list with counts |
| `POST /accounts` `{platform, username}` | validates on the platform; 422 if unknown user; 409 if already linked |
| `DELETE /accounts/{id}` | deletes the account and its games/analyses/jobs |
| `POST /accounts/{id}/sync` `{months?}` | enqueue sync job → job |
| `POST /accounts/sync-all` | enqueue sync for every account → jobs[] |
| `GET /games` | query: `account_id, platform, time_class, user_result, color, analysis_status, search (opponent), from, to, sort (played_at\|accuracy\|rating), order, page, page_size(≤200)` → `{items, total, page, page_size}` (items exclude `pgn`; include summary accuracy if analysed) |
| `GET /games/{id}` | full game incl. `pgn` |
| `GET /games/{id}/analysis` | analysis row (404 if none) |
| `POST /games/{id}/analyze` `{force?}` | enqueue; 409 if already done and not `force` |
| `POST /games/analyze` `{game_ids}` | bulk enqueue → `{jobs, skipped}` |
| `DELETE /games/{id}/analysis` | remove analysis, status → `none` |
| `GET /jobs?status=` | list (newest first, ≤200) |
| `GET /jobs/{id}` · `POST /jobs/{id}/cancel` · `POST /jobs/cancel-all` · `DELETE /jobs/finished` | |
| `GET /stats/overview` | totals, analysed count, mean accuracy, win/draw/loss counts |
| `GET /stats/accuracy-trend?bucket=week\|month&account_id=` | `[{bucket, games, accuracy}]` |
| `GET /stats/by-time-class` | per class: games, win rate, mean accuracy, blunders per game |
| `GET /stats/openings?color=&limit=` | `[{eco, name, games, win_rate}]` |
| `GET /stats/results` | win/draw/loss by colour |
| `GET /settings` · `PATCH /settings` | validated; engine changes trigger session restart |
| `GET /system` | cpu, memory, recommendations, engine `{path, valid, version, message}` |
| `POST /system/engine/validate` `{path}` | runs `uci`, returns name/version |
| `GET /database/export` | downloads `lca.db` after WAL checkpoint |
| `POST /database/import` | multipart; validates schema; backs up current file |
| `POST /database/reset` | deletes all data, keeps settings |
| `GET /events` | SSE stream |

Frontend and backend share the same origin in every deployment (FastAPI static mount, or nginx proxy), so CORS is only enabled for the Vite dev origin.

---

## 9. Frontend

### 9.1 Stack
Svelte 5 (runes), TypeScript, Vite 7. Runtime deps: `chessground`, `chess.js`. No router, chart, or CSS framework dependencies. `svelte-check` in CI.

### 9.2 Design system (`styles/tokens.css`)
- **Dark-first.** `:root` defines the dark palette; `[data-theme="light"]` overrides; `system` maps via `prefers-color-scheme`.
- Neutrals: bg `#0e1013`, surface `#15181d`, raised `#1c2027`, border `#262b33`, text `#e6e8eb`, muted `#8b929c`. Accent `#7cb342` (green, used sparingly for primary actions). Danger `#e5484d`.
- Classification colours (chess.com convention): brilliant `#1baca6`, great `#5b8bb0`, best `#81b64c`, excellent `#96bc4b`, good `#95b776`, book `#a88865`, inaccuracy `#f7c631`, mistake `#e58f2a`, miss `#ee6b55`, blunder `#ca3431`, forced `#8b929c`.
- Type: system stack (`-apple-system, "Segoe UI", Inter, Roboto, sans-serif`); mono for evals/clocks (`ui-monospace, "SF Mono", Menlo, monospace`). Scale 12/13/14/16/20/28.
- Space scale 4/8/12/16/24/32. Radius 6/10. Focus ring visible on all interactive elements.
- Board: chessground with a custom colour set (light `#d5d0c3`, dark `#6f7f6b`) and highlights tuned for dark surfaces; classification icon overlaid on the destination square; best-move arrow.

### 9.3 Shell
Left sidebar (Dashboard, Games, Accounts, Settings) + **JobsTray** at the bottom showing active/queued jobs with progress bars and cancel; collapses to a top bar with a sheet menu under 900 px. Toasts top-right. Global keyboard: `←/→/Home/End` in review, `/` focuses search on Games.

### 9.4 Routes
- `#/setup` — first run (no accounts): 1) add account (platform + username, validated live), 2) engine tuning with recommendations from `/system`, 3) start first sync → progress → "Go to games". Sets `setup_completed`.
- `#/` **Dashboard** — stat tiles (games, analysed, mean accuracy, win rate), accuracy trend line, results-by-colour bars, blunders-per-game by time class, top openings, recent games. Account filter.
- `#/games` **Games** — FilterBar (account, platform, time class, result, colour, analysis status, date range, opponent search), sortable table, pagination, multi-select → analyze; row shows opponent + rating, colour played, result pill, time class, date, accuracy, status.
- `#/games/:id` **GameReview** — header (players, ratings, result, termination, opening, platform link); left column: EvalBar + Board (oriented to `user_color`) + player rows with clocks + nav controls; right column: ReportCard (both accuracies, counts with icons; chess.com's accuracy shown when available), EvalGraph (click/drag to seek, classification markers), MoveList (two-column, icon per move, auto-scroll), MoveDetail (label, "best was …", engine line, eval). If not analysed: Analyze button → progress → auto-load on completion via SSE.
- `#/accounts` — cards per account (platform badge, username, game count, last synced, sync with optional month limit, delete with Dialog confirm); add form.
- `#/settings` — engine (path + validate + version, threads/hash with recommended values, depth/time), behaviour (auto-analyze), appearance (theme), data (export/import/reset), about.

### 9.5 State
- `stores/jobs.svelte.ts` holds the job list, fed by `GET /jobs` then patched by SSE.
- `stores/settings.svelte.ts`, `stores/accounts.svelte.ts` load once, expose `refresh()`.
- Page-local state stays in the page component; shared derived logic in `lib/chess`.

---

## 10. Packaging and CI

- **PyInstaller** spec: entry `backend/lca/cli.py`; datas: `frontend/dist → frontend_dist`, `stockfish/`, `backend/lca/data → lca/data`; `pathex=["backend"]`. Data dir resolution unchanged (`data/` next to the executable). DB file `lca.db` — an old `games.db` is left untouched.
- **Docker**: backend image installs with `uv`; frontend image unchanged (nginx serves `dist`, proxies `/api`). `docker-compose.yml` unchanged apart from the backend build context.
- **release.yml**: update backend install (`uv sync`) and frontend build steps; tagging logic unchanged.
- Dev: `cd backend && uv run uvicorn lca.main:app --reload --port 42069` and `cd frontend && npm run dev` (Vite proxies `/api` → 42069, so no `VITE_API_BASE_URL`).

---

## 11. Testing

- **domain/**: table-driven tests per classification with crafted FENs and synthetic evals (Greek gift → Brilliant; only move → Great; missed mate → Miss; opening line → Book; single legal move → Forced; SEE cases from §5.4.1; accuracy formula vectors; opening lookup).
- **platforms/**: fixtures recorded from the real responses captured on 2026-09-15 (`tests/fixtures/chesscom_archive.json`, `lichess_games.ndjson`); `httpx.MockTransport`; variant filtering, cursor logic, mapping.
- **services/analysis**: fake engine returning scripted lines; asserts MoveRecord shape, counts, progress callbacks, cancellation.
- **api/**: `httpx.AsyncClient` against `create_app()` with a temp DB; runner started with a fake engine; SSE smoke test.
- **frontend/**: vitest for `lib/chess/*` and the router; `svelte-check` in CI.

---

## 12. Error handling
- Engine missing/invalid: `/system` reports it; analyze jobs fail fast with `engine_unavailable`; Settings page surfaces the fix.
- Platform errors: `user_not_found` (422 on add), `rate_limited` (job waits `Retry-After` then resumes, up to 3 times), network errors fail the job with a message; partial progress is kept (games already upserted stay; cursor only advances on success).
- Corrupt PGN: game imported but analyze fails with `invalid_pgn`.
- Engine crash mid-game: session restarts once; the job retries the current ply once, then fails.
