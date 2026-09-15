"""Persistent job queue with one serial lane per job kind, plus an in-memory event bus."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select, update

from ..db.engine import SessionFactory
from ..db.models import Job, utcnow_iso

log = logging.getLogger(__name__)

ACTIVE_STATUSES = ("queued", "running")
FINISHED_STATUSES = ("done", "failed", "cancelled")


class JobCancelled(Exception):
    pass


def job_to_dict(job: Job) -> dict[str, Any]:
    return {
        "id": job.id,
        "kind": job.kind,
        "game_id": job.game_id,
        "account_id": job.account_id,
        "params": job.params,
        "status": job.status,
        "progress": job.progress,
        "total": job.total,
        "message": job.message,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
    }


class EventBus:
    def __init__(self, maxsize: int = 500):
        self._subscribers: set[asyncio.Queue[dict[str, Any]]] = set()
        self._maxsize = maxsize

    def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        q: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=self._maxsize)
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue[dict[str, Any]]) -> None:
        self._subscribers.discard(q)

    def publish(self, event: str, data: dict[str, Any]) -> None:
        msg = {"event": event, "data": data}
        for q in list(self._subscribers):
            if q.full():
                with contextlib.suppress(asyncio.QueueEmpty):
                    q.get_nowait()
            q.put_nowait(msg)


@dataclass
class JobContext:
    runner: JobRunner
    job: Job

    async def progress(self, done: int, total: int, message: str | None = None) -> None:
        await self.runner.update_progress(self.job.id, done, total, message)

    def is_cancelled(self) -> bool:
        return self.runner.is_cancelled(self.job.id)

    def raise_if_cancelled(self) -> None:
        if self.is_cancelled():
            raise JobCancelled()


Handler = Callable[[Job, JobContext], Awaitable[None]]
CancelHook = Callable[[Job], Awaitable[None]]


class JobRunner:
    def __init__(
        self,
        session_factory: SessionFactory,
        bus: EventBus,
        handlers: dict[str, Handler],
        *,
        lanes: dict[str, str] | None = None,
        on_cancelled: CancelHook | None = None,
    ):
        self._sf = session_factory
        self._bus = bus
        self._handlers = handlers
        # Called for jobs cancelled while still queued; running jobs clean up in their handler.
        self._on_cancelled = on_cancelled
        self._lanes = lanes or {"analyze": "analysis", "sync": "sync"}
        self._tasks: list[asyncio.Task[None]] = []
        self._wake: dict[str, asyncio.Event] = {
            ln: asyncio.Event() for ln in set(self._lanes.values())
        }
        self._cancelled: set[int] = set()
        self._running: dict[int, str] = {}  # job id -> lane
        self._stopping = False

    # ---- lifecycle -------------------------------------------------------------------

    async def start(self) -> None:
        self._stopping = False
        for lane in set(self._lanes.values()):
            self._wake[lane].set()
            self._tasks.append(asyncio.create_task(self._lane_loop(lane), name=f"lane:{lane}"))

    async def stop(self) -> None:
        self._stopping = True
        for t in self._tasks:
            t.cancel()
        for t in self._tasks:
            with contextlib.suppress(asyncio.CancelledError):
                await t
        self._tasks.clear()

    # ---- public API ------------------------------------------------------------------

    async def enqueue(
        self,
        kind: str,
        *,
        game_id: int | None = None,
        account_id: int | None = None,
        params: dict[str, Any] | None = None,
    ) -> Job:
        if kind not in self._lanes:
            raise ValueError(f"unknown job kind: {kind}")
        async with self._sf() as session:
            stmt = select(Job).where(Job.kind == kind, Job.status.in_(ACTIVE_STATUSES))
            if game_id is not None:
                stmt = stmt.where(Job.game_id == game_id)
            if account_id is not None:
                stmt = stmt.where(Job.account_id == account_id)
            if game_id is not None or account_id is not None:
                existing = (await session.execute(stmt)).scalars().first()
                if existing is not None:
                    return existing
            job = Job(kind=kind, game_id=game_id, account_id=account_id, params=params)
            session.add(job)
            await session.commit()
            await session.refresh(job)
        self._bus.publish("job", job_to_dict(job))
        self._wake[self._lanes[kind]].set()
        return job

    async def get(self, job_id: int) -> Job | None:
        async with self._sf() as session:
            return await session.get(Job, job_id)

    async def list(self, status: str | None = None, limit: int = 200) -> list[Job]:
        async with self._sf() as session:
            stmt = select(Job).order_by(Job.id.desc()).limit(limit)
            if status == "active":
                stmt = stmt.where(Job.status.in_(ACTIVE_STATUSES))
            elif status:
                stmt = stmt.where(Job.status == status)
            return list((await session.execute(stmt)).scalars().all())

    async def cancel(self, job_id: int) -> bool:
        async with self._sf() as session:
            job = await session.get(Job, job_id)
            if job is None or job.status not in ACTIVE_STATUSES:
                return False
            if job.status == "queued":
                job.status = "cancelled"
                job.finished_at = utcnow_iso()
                await session.commit()
                self._bus.publish("job", job_to_dict(job))
                if self._on_cancelled is not None:
                    await self._on_cancelled(job)
                return True
        self._cancelled.add(job_id)
        return True

    async def cancel_all(self) -> int:
        jobs = await self.list("active")
        n = 0
        for job in jobs:
            if await self.cancel(job.id):
                n += 1
        return n

    async def clear_finished(self) -> int:
        async with self._sf() as session:
            result = await session.execute(
                Job.__table__.delete().where(Job.status.in_(FINISHED_STATUSES))
            )
            await session.commit()
            return int(result.rowcount or 0)

    def is_cancelled(self, job_id: int) -> bool:
        return job_id in self._cancelled or self._stopping

    async def update_progress(
        self, job_id: int, progress: int, total: int, message: str | None = None
    ) -> None:
        async with self._sf() as session:
            values: dict[str, Any] = {"progress": progress, "total": total}
            if message is not None:
                values["message"] = message
            await session.execute(update(Job).where(Job.id == job_id).values(**values))
            await session.commit()
            job = await session.get(Job, job_id)
        if job is not None:
            self._bus.publish("job", job_to_dict(job))

    # ---- lane loop -------------------------------------------------------------------

    def _kinds_for(self, lane: str) -> list[str]:
        return [k for k, ln in self._lanes.items() if ln == lane]

    async def _next_job(self, lane: str) -> Job | None:
        async with self._sf() as session:
            stmt = (
                select(Job)
                .where(Job.kind.in_(self._kinds_for(lane)), Job.status == "queued")
                .order_by(Job.id.asc())
                .limit(1)
            )
            return (await session.execute(stmt)).scalars().first()

    async def _lane_loop(self, lane: str) -> None:
        wake = self._wake[lane]
        while True:
            job = await self._next_job(lane)
            if job is None:
                wake.clear()
                with contextlib.suppress(TimeoutError):
                    await asyncio.wait_for(wake.wait(), timeout=2.0)
                continue
            await self._run(job, lane)

    async def _set_status(self, job_id: int, status: str, message: str | None = None) -> Job:
        async with self._sf() as session:
            job = await session.get(Job, job_id)
            assert job is not None
            job.status = status
            now = utcnow_iso()
            if status == "running":
                job.started_at = now
            else:
                job.finished_at = now
            if message is not None:
                job.message = message
            await session.commit()
            await session.refresh(job)
        self._bus.publish("job", job_to_dict(job))
        return job

    async def _run(self, job: Job, lane: str) -> None:
        handler = self._handlers.get(job.kind)
        if handler is None:
            await self._set_status(job.id, "failed", f"no handler for {job.kind}")
            return
        self._running[job.id] = lane
        job = await self._set_status(job.id, "running")
        ctx = JobContext(runner=self, job=job)
        try:
            await handler(job, ctx)
        except JobCancelled:
            await self._set_status(job.id, "cancelled", "Cancelled")
        except asyncio.CancelledError:
            await self._set_status(job.id, "queued", "Interrupted by shutdown")
            raise
        except Exception as e:  # noqa: BLE001 - job failures are reported, not raised
            log.exception("Job %s failed", job.id)
            await self._set_status(job.id, "failed", str(e) or e.__class__.__name__)
        else:
            if self.is_cancelled(job.id):
                await self._set_status(job.id, "cancelled", "Cancelled")
            else:
                await self._set_status(job.id, "done", None)
        finally:
            self._running.pop(job.id, None)
            self._cancelled.discard(job.id)
