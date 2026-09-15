async def test_health(client):
    r = await client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["version"] == "2.0.0"


async def test_unknown_route_returns_json_error(client):
    r = await client.get("/api/nope")
    assert r.status_code == 404
