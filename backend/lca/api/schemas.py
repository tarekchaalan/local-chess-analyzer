"""Pydantic response/request models shared by all routers."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Platform = Literal["chesscom", "lichess"]


class HealthOut(BaseModel):
    ok: bool
    version: str


# ---- accounts ------------------------------------------------------------------------


class AccountOut(BaseModel):
    id: int
    platform: str
    username: str
    created_at: str
    last_synced_at: str | None
    game_count: int
    analyzed_count: int = 0


class AccountCreate(BaseModel):
    platform: Platform
    username: str = Field(min_length=1, max_length=64)


class SyncRequest(BaseModel):
    months: int | None = Field(default=None, ge=1, le=600)


# ---- jobs ----------------------------------------------------------------------------


class JobOut(BaseModel):
    id: int
    kind: str
    game_id: int | None
    account_id: int | None
    params: dict[str, Any] | None
    status: str
    progress: int
    total: int
    message: str | None
    created_at: str
    started_at: str | None
    finished_at: str | None


class CountOut(BaseModel):
    count: int


# ---- games ---------------------------------------------------------------------------


class GameListItem(BaseModel):
    id: int
    account_id: int
    platform: str
    platform_game_id: str
    url: str | None
    white: str
    black: str
    white_rating: int | None
    black_rating: int | None
    user_color: str
    result: str
    user_result: str
    termination: str | None
    time_class: str
    time_control: str | None
    rated: bool
    played_at: str
    eco: str | None
    opening_name: str | None
    ply_count: int
    analysis_status: str
    accuracy: float | None = None  # the user's accuracy, when analysed
    opponent: str
    opponent_rating: int | None
    user_rating: int | None


class GameOut(GameListItem):
    pgn: str
    platform_accuracy_white: float | None
    platform_accuracy_black: float | None
    imported_at: str


class GameListResponse(BaseModel):
    items: list[GameListItem]
    total: int
    page: int
    page_size: int


class AnalysisOut(BaseModel):
    game_id: int
    engine_name: str
    depth: int
    time_ms: int
    multipv: int
    threads: int
    hash_mb: int
    created_at: str
    accuracy_white: float
    accuracy_black: float
    opening_eco: str | None
    opening_name: str | None
    book_plies: int
    counts: dict[str, dict[str, int]]
    moves: list[dict[str, Any]]


class AnalyzeRequest(BaseModel):
    force: bool = False


class BulkAnalyzeRequest(BaseModel):
    game_ids: list[int] = Field(min_length=1, max_length=5000)
    force: bool = False


class BulkAnalyzeResponse(BaseModel):
    jobs: list[JobOut]
    skipped: list[int]


# ---- stats ---------------------------------------------------------------------------


class ResultCounts(BaseModel):
    games: int
    wins: int
    draws: int
    losses: int
    win_rate: float | None


class OverviewOut(ResultCounts):
    analyzed: int
    mean_accuracy: float | None
    accounts: int


class TrendPoint(BaseModel):
    bucket: str
    games: int
    accuracy: float


class TimeClassStat(ResultCounts):
    time_class: str
    analyzed: int
    mean_accuracy: float | None
    blunders_per_game: float | None
    mistakes_per_game: float | None


class OpeningStat(ResultCounts):
    eco: str | None
    name: str


class ResultsByColorOut(BaseModel):
    white: ResultCounts
    black: ResultCounts


# ---- settings / system / database ----------------------------------------------------


class SettingsUpdateOut(BaseModel):
    updated: list[str]
    settings: dict[str, str]


class CpuInfo(BaseModel):
    physical_cores: int
    logical_cores: int
    usage_percent: float
    recommended_threads: int


class MemoryInfo(BaseModel):
    total_mb: int
    available_mb: int
    used_mb: int
    usage_percent: float
    recommended_hash_mb: int


class EngineInfo(BaseModel):
    path: str
    exists: bool
    valid: bool
    name: str | None
    message: str
    bundled_path: str | None = None
    custom_path: str | None = None
    is_bundled: bool = True


class SystemOut(BaseModel):
    cpu: CpuInfo
    memory: MemoryInfo
    engine: EngineInfo
    recommended_depth: int
    platform: str


class EngineValidateRequest(BaseModel):
    path: str = Field(min_length=1, max_length=1024)


class DatabaseImportOut(BaseModel):
    games: int
    accounts: int
    backup_path: str | None


class DatabaseResetOut(BaseModel):
    deleted_games: int
    deleted_accounts: int
