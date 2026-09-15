"""Host resources and engine validation."""

from __future__ import annotations

import platform
import time
from pathlib import Path

import psutil

from ..api.schemas import CpuInfo, EngineInfo, MemoryInfo, SystemOut
from .engine import EngineSession
from .settings import recommended_hash_mb, recommended_threads

_validation_cache: dict[str, tuple[float, float, dict]] = {}  # path -> (mtime, checked_at, result)
_CACHE_TTL = 120.0


async def validate_engine(path: str) -> EngineInfo:
    p = Path(path)
    exists = p.exists()
    mtime = p.stat().st_mtime if exists else -1.0
    cached = _validation_cache.get(path)
    now = time.monotonic()
    if cached and cached[0] == mtime and now - cached[1] < _CACHE_TTL:
        result = cached[2]
    else:
        result = await EngineSession.validate(path)
        _validation_cache[path] = (mtime, now, result)
    return EngineInfo(
        path=path,
        exists=exists,
        valid=bool(result["valid"]),
        name=result.get("name"),
        message=result["message"],
    )


def cpu_info() -> CpuInfo:
    return CpuInfo(
        physical_cores=psutil.cpu_count(logical=False) or 1,
        logical_cores=psutil.cpu_count(logical=True) or 1,
        usage_percent=psutil.cpu_percent(interval=None),
        recommended_threads=recommended_threads(),
    )


def memory_info() -> MemoryInfo:
    mem = psutil.virtual_memory()
    mb = 1024 * 1024
    return MemoryInfo(
        total_mb=int(mem.total / mb),
        available_mb=int(mem.available / mb),
        used_mb=int(mem.used / mb),
        usage_percent=mem.percent,
        recommended_hash_mb=recommended_hash_mb(),
    )


def recommended_depth(threads: int) -> int:
    if threads >= 8:
        return 20
    if threads >= 4:
        return 18
    return 15


async def system_info(engine_path: str) -> SystemOut:
    cpu = cpu_info()
    return SystemOut(
        cpu=cpu,
        memory=memory_info(),
        engine=await validate_engine(engine_path),
        recommended_depth=recommended_depth(cpu.recommended_threads),
        platform=f"{platform.system()} {platform.machine()}",
    )
