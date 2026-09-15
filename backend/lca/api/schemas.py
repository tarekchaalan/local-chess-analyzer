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
