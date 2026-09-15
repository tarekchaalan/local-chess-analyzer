"""Server-Sent Events stream of job / game / account updates."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

router = APIRouter(tags=["events"])


@router.get("/events")
async def events(request: Request) -> EventSourceResponse:
    bus = request.app.state.bus
    queue = bus.subscribe()

    async def stream():
        try:
            yield {"event": "ready", "data": "{}"}
            while True:
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=1.0)
                except TimeoutError:
                    continue
                yield {"event": msg["event"], "data": json.dumps(msg["data"])}
        finally:
            bus.unsubscribe(queue)

    return EventSourceResponse(stream(), ping=15)
