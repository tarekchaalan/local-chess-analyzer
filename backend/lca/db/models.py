"""SQLAlchemy 2.0 models. Timestamps are stored as UTC ISO-8601 strings."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("platform", "username_key", name="uq_account_platform_user"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    platform: Mapped[str] = mapped_column(String(16), nullable=False)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    username_key: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default=utcnow_iso)
    last_synced_at: Mapped[str | None] = mapped_column(String(32))
    sync_cursor: Mapped[str | None] = mapped_column(String(64))
    game_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Game(Base):
    __tablename__ = "games"
    __table_args__ = (
        UniqueConstraint("platform", "platform_game_id", name="uq_game_platform_id"),
        Index("ix_games_account_id", "account_id"),
        Index("ix_games_played_at", "played_at"),
        Index("ix_games_time_class", "time_class"),
        Index("ix_games_analysis_status", "analysis_status"),
        Index("ix_games_user_result", "user_result"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    platform: Mapped[str] = mapped_column(String(16), nullable=False)
    platform_game_id: Mapped[str] = mapped_column(String(64), nullable=False)
    url: Mapped[str | None] = mapped_column(String(256))
    pgn: Mapped[str] = mapped_column(Text, nullable=False)
    white: Mapped[str] = mapped_column(String(64), nullable=False)
    black: Mapped[str] = mapped_column(String(64), nullable=False)
    white_rating: Mapped[int | None] = mapped_column(Integer)
    black_rating: Mapped[int | None] = mapped_column(Integer)
    user_color: Mapped[str] = mapped_column(String(1), nullable=False)  # w | b
    result: Mapped[str] = mapped_column(String(8), nullable=False)  # 1-0 | 0-1 | 1/2-1/2
    user_result: Mapped[str] = mapped_column(String(8), nullable=False)  # win | loss | draw
    termination: Mapped[str | None] = mapped_column(String(64))
    time_class: Mapped[str] = mapped_column(String(16), nullable=False)
    time_control: Mapped[str | None] = mapped_column(String(32))
    rated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    played_at: Mapped[str] = mapped_column(String(32), nullable=False)
    eco: Mapped[str | None] = mapped_column(String(8))
    opening_name: Mapped[str | None] = mapped_column(String(128))
    platform_accuracy_white: Mapped[float | None] = mapped_column(Float)
    platform_accuracy_black: Mapped[float | None] = mapped_column(Float)
    ply_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    imported_at: Mapped[str] = mapped_column(String(32), nullable=False, default=utcnow_iso)
    analysis_status: Mapped[str] = mapped_column(String(16), nullable=False, default="none")


class Analysis(Base):
    __tablename__ = "analyses"

    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"), primary_key=True
    )
    engine_name: Mapped[str] = mapped_column(String(64), nullable=False)
    depth: Mapped[int] = mapped_column(Integer, nullable=False)
    time_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    multipv: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    threads: Mapped[int] = mapped_column(Integer, nullable=False)
    hash_mb: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default=utcnow_iso)
    accuracy_white: Mapped[float] = mapped_column(Float, nullable=False)
    accuracy_black: Mapped[float] = mapped_column(Float, nullable=False)
    opening_eco: Mapped[str | None] = mapped_column(String(8))
    opening_name: Mapped[str | None] = mapped_column(String(128))
    book_plies: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    counts: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    moves: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (Index("ix_jobs_status_kind", "status", "kind"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)  # analyze | sync
    game_id: Mapped[int | None] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"))
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"))
    params: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="queued")
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False, default=utcnow_iso)
    started_at: Mapped[str | None] = mapped_column(String(32))
    finished_at: Mapped[str | None] = mapped_column(String(32))


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
