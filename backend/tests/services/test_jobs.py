import asyncio

import pytest

from lca.db.bootstrap import init_db
from lca.db.engine import make_engine, make_session_factory
from lca.db.models import Account, Game
from lca.services.jobs import EventBus, JobCancelled, JobRunner


@pytest.fixture
async def sf(tmp_path):
    engine = make_engine(tmp_path / "t.db")
    await init_db(engine)
    factory = make_session_factory(engine)
    async with factory() as s:
        acc = Account(platform="chesscom", username="u", username_key="u")
        s.add(acc)
        await s.flush()
        for i in range(3):
            s.add(
                Game(
                    account_id=acc.id,
                    platform="chesscom",
                    platform_game_id=f"g{i}",
                    pgn="1. e4 *",
                    white="u",
                    black="v",
                    user_color="w",
                    result="1-0",
                    user_result="win",
                    time_class="blitz",
                    played_at="2025-01-01T00:00:00Z",
                )  # fmt: skip
            )
        await s.commit()
    yield factory
    await engine.dispose()


async def _wait_for(pred, timeout=5.0):
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        if await pred():
            return True
        await asyncio.sleep(0.02)
    return False


async def test_fifo_serial_execution_and_events(sf):
    bus = EventBus()
    q = bus.subscribe()
    order: list[int] = []
    gate = asyncio.Event()

    async def handler(job, ctx):
        order.append(job.game_id)
        await gate.wait()

    runner = JobRunner(sf, bus, {"analyze": handler})
    await runner.start()
    try:
        j1 = await runner.enqueue("analyze", game_id=1)
        j2 = await runner.enqueue("analyze", game_id=2)
        assert j1.id != j2.id
        assert await _wait_for(lambda: asyncio.sleep(0, result=order == [1]))
        # second is still queued while first runs
        assert (await runner.get(j2.id)).status == "queued"
        gate.set()
        assert await _wait_for(lambda: asyncio.sleep(0, result=order == [1, 2]))
        assert await _wait_for(lambda: _status_is(runner, j2.id, "done"))
    finally:
        await runner.stop()
    statuses = []
    while not q.empty():
        msg = q.get_nowait()
        assert msg["event"] == "job"
        statuses.append((msg["data"]["id"], msg["data"]["status"]))
    assert (j1.id, "running") in statuses and (j1.id, "done") in statuses


async def _status_is(runner, job_id, status):
    job = await runner.get(job_id)
    return job is not None and job.status == status


async def test_dedupe_per_game(sf):
    runner = JobRunner(sf, EventBus(), {"analyze": _noop})
    a = await runner.enqueue("analyze", game_id=1)
    b = await runner.enqueue("analyze", game_id=1)
    assert a.id == b.id


async def _noop(job, ctx):
    return None


async def test_cancel_queued_job(sf):
    runner = JobRunner(sf, EventBus(), {"analyze": _noop})
    job = await runner.enqueue("analyze", game_id=1)  # runner not started
    assert await runner.cancel(job.id)
    assert (await runner.get(job.id)).status == "cancelled"
    assert not await runner.cancel(job.id)


async def test_cancel_running_job(sf):
    started = asyncio.Event()

    async def handler(job, ctx):
        started.set()
        while True:
            ctx.raise_if_cancelled()
            await asyncio.sleep(0.01)

    runner = JobRunner(sf, EventBus(), {"analyze": handler})
    await runner.start()
    try:
        job = await runner.enqueue("analyze", game_id=1)
        await asyncio.wait_for(started.wait(), 5)
        assert await runner.cancel(job.id)
        assert await _wait_for(lambda: _status_is(runner, job.id, "cancelled"))
    finally:
        await runner.stop()


async def test_failure_is_recorded(sf):
    async def handler(job, ctx):
        raise RuntimeError("boom")

    runner = JobRunner(sf, EventBus(), {"analyze": handler})
    await runner.start()
    try:
        job = await runner.enqueue("analyze", game_id=1)
        assert await _wait_for(lambda: _status_is(runner, job.id, "failed"))
        assert (await runner.get(job.id)).message == "boom"
    finally:
        await runner.stop()


async def test_progress_updates(sf):
    bus = EventBus()
    q = bus.subscribe()

    async def handler(job, ctx):
        await ctx.progress(3, 10, "working")

    runner = JobRunner(sf, bus, {"analyze": handler})
    await runner.start()
    try:
        job = await runner.enqueue("analyze", game_id=1)
        assert await _wait_for(lambda: _status_is(runner, job.id, "done"))
        final = await runner.get(job.id)
        assert (final.progress, final.total, final.message) == (3, 10, "working")
    finally:
        await runner.stop()
    events = []
    while not q.empty():
        events.append(q.get_nowait()["data"])
    assert any(e["progress"] == 3 for e in events)


async def test_lanes_run_concurrently(sf):
    both = asyncio.Barrier(2)

    async def handler(job, ctx):
        await asyncio.wait_for(both.wait(), 5)

    runner = JobRunner(sf, EventBus(), {"analyze": handler, "sync": handler})
    await runner.start()
    try:
        a = await runner.enqueue("analyze", game_id=1)
        s = await runner.enqueue("sync", account_id=1)
        assert await _wait_for(lambda: _status_is(runner, a.id, "done"))
        assert await _wait_for(lambda: _status_is(runner, s.id, "done"))
    finally:
        await runner.stop()


async def test_job_cancelled_exception_type():
    assert issubclass(JobCancelled, Exception)


async def test_cancel_hook_runs_for_queued_jobs_only(sf):
    seen = []

    async def hook(job):
        seen.append((job.id, job.status))

    runner = JobRunner(sf, EventBus(), {"analyze": _noop}, on_cancelled=hook)
    job = await runner.enqueue("analyze", game_id=1)  # runner not started -> stays queued
    assert await runner.cancel(job.id)
    assert seen == [(job.id, "cancelled")]
