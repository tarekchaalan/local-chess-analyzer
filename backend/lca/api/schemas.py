"""Pydantic response/request models shared by all routers."""

from __future__ import annotations

from pydantic import BaseModel


class HealthOut(BaseModel):
    ok: bool
    version: str
