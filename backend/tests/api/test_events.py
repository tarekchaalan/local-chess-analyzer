import asyncio
import socket

import httpx
import uvicorn


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


async def test_sse_streams_job_events(app):
    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning", lifespan="on")
    server = uvicorn.Server(config)
    serve_task = asyncio.create_task(server.serve())
    try:
        async with httpx.AsyncClient(base_url=f"http://127.0.0.1:{port}", timeout=10) as client:
            for _ in range(100):
                try:
                    if (await client.get("/api/health")).status_code == 200:
                        break
                except httpx.HTTPError:
                    await asyncio.sleep(0.05)
            acc = (
                await client.post(
                    "/api/accounts", json={"platform": "chesscom", "username": "hikaru"}
                )
            ).json()

            async def read_events():
                seen = []
                async with client.stream("GET", "/api/events") as r:
                    assert r.status_code == 200
                    assert r.headers["content-type"].startswith("text/event-stream")
                    async for line in r.aiter_lines():
                        if line.startswith("event:"):
                            seen.append(line.split(":", 1)[1].strip())
                        if "job" in seen and "account" in seen:
                            break
                return seen

            reader = asyncio.create_task(read_events())
            await asyncio.sleep(0.2)
            await client.post(f"/api/accounts/{acc['id']}/sync")
            seen = await asyncio.wait_for(reader, timeout=10)
            assert seen[0] == "ready"
            assert "job" in seen and "account" in seen
    finally:
        server.should_exit = True
        await asyncio.wait_for(serve_task, timeout=10)
