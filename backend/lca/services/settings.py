"""Typed access to the key/value settings table, with defaults and validation."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import psutil
from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert

from ..config import Paths
from ..db.engine import SessionFactory
from ..db.models import Setting

THEMES = ("dark", "light", "system")


@dataclass(frozen=True)
class SettingSpec:
    default: Callable[[Paths], str]
    validate: Callable[[str], str]  # returns normalized value or raises ValueError


def _int_in(lo: int, hi: int) -> Callable[[str], str]:
    def check(v: str) -> str:
        try:
            n = int(v)
        except (TypeError, ValueError):
            raise ValueError(f"must be an integer between {lo} and {hi}") from None
        if not lo <= n <= hi:
            raise ValueError(f"must be between {lo} and {hi}")
        return str(n)

    return check


def _bool(v: str) -> str:
    s = str(v).strip().lower()
    if s in ("true", "1", "yes", "on"):
        return "true"
    if s in ("false", "0", "no", "off", ""):
        return "false"
    raise ValueError("must be true or false")


def _theme(v: str) -> str:
    if v not in THEMES:
        raise ValueError(f"must be one of {', '.join(THEMES)}")
    return v


def _text(max_len: int) -> Callable[[str], str]:
    def check(v: str) -> str:
        s = str(v)
        if len(s) > max_len:
            raise ValueError(f"must be at most {max_len} characters")
        return s

    return check


def recommended_threads() -> int:
    logical = psutil.cpu_count(logical=True) or 1
    return max(1, logical - 2)


def recommended_hash_mb() -> int:
    available_mb = int(psutil.virtual_memory().available / (1024 * 1024))
    return max(128, min(int(available_mb * 0.15), 2048))


SPECS: dict[str, SettingSpec] = {
    # Empty means "the bundled Stockfish", resolved at runtime so the library can move.
    "engine_path": SettingSpec(lambda _: "", _text(1024)),
    "engine_threads": SettingSpec(lambda _: str(recommended_threads()), _int_in(1, 128)),
    "engine_hash_mb": SettingSpec(lambda _: str(recommended_hash_mb()), _int_in(16, 16384)),
    "analysis_depth": SettingSpec(lambda _: "18", _int_in(1, 60)),
    "analysis_time_ms": SettingSpec(lambda _: "2000", _int_in(0, 600_000)),
    "auto_analyze_new_games": SettingSpec(lambda _: "false", _bool),
    "theme": SettingSpec(lambda _: "system", _theme),
    "lichess_token": SettingSpec(lambda _: "", _text(256)),
    "setup_completed": SettingSpec(lambda _: "false", _bool),
}

ENGINE_KEYS = frozenset({"engine_path", "engine_threads", "engine_hash_mb"})


class SettingsService:
    def __init__(self, session_factory: SessionFactory, paths: Paths):
        self._sf = session_factory
        self._paths = paths
        self._cache: dict[str, str] | None = None

    def defaults(self) -> dict[str, str]:
        return {k: spec.default(self._paths) for k, spec in SPECS.items()}

    async def get_all(self) -> dict[str, str]:
        if self._cache is None:
            async with self._sf() as session:
                rows = (await session.execute(select(Setting))).scalars().all()
            stored = {r.key: r.value for r in rows if r.key in SPECS}
            self._cache = {**self.defaults(), **stored}
        return dict(self._cache)

    async def get(self, key: str) -> str:
        return (await self.get_all())[key]

    async def get_int(self, key: str) -> int:
        return int(await self.get(key))

    async def get_bool(self, key: str) -> bool:
        return (await self.get(key)) == "true"

    def bundled_engine_path(self) -> str:
        return str(self._paths.default_engine_path())

    async def engine_path(self) -> str:
        """The engine to run: a custom path if set and present, else the bundled binary."""
        custom = (await self.get("engine_path")).strip()
        if custom and Path(custom).exists():
            return custom
        return self.bundled_engine_path()

    async def update(self, values: dict[str, object]) -> list[str]:
        """Validate and persist. Returns the keys that were written."""
        normalized: dict[str, str] = {}
        errors: dict[str, str] = {}
        for key, raw in values.items():
            spec = SPECS.get(key)
            if spec is None:
                errors[key] = "unknown setting"
                continue
            try:
                normalized[key] = spec.validate("" if raw is None else str(raw))
            except ValueError as e:
                errors[key] = str(e)
        if errors:
            raise SettingsValidationError(errors)
        if normalized.get("engine_path", None) == self.bundled_engine_path():
            normalized["engine_path"] = ""
        if not normalized:
            return []
        async with self._sf() as session:
            for key, value in normalized.items():
                stmt = insert(Setting).values(key=key, value=value)
                stmt = stmt.on_conflict_do_update(index_elements=["key"], set_={"value": value})
                await session.execute(stmt)
            await session.commit()
        self._cache = None
        return list(normalized)


class SettingsValidationError(ValueError):
    def __init__(self, errors: dict[str, str]):
        super().__init__("invalid settings")
        self.errors = errors
