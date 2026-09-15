from ..conftest import wait_for_job


async def test_add_list_delete_account(client):
    r = await client.post("/api/accounts", json={"platform": "chesscom", "username": "HIKARU"})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["username"] == "Hikaru" and body["platform"] == "chesscom"
    assert body["game_count"] == 0

    r = await client.get("/api/accounts")
    assert [a["id"] for a in r.json()] == [body["id"]]

    r = await client.delete(f"/api/accounts/{body['id']}")
    assert r.status_code == 204
    assert (await client.get("/api/accounts")).json() == []


async def test_unknown_user_is_422(client):
    r = await client.post("/api/accounts", json={"platform": "lichess", "username": "nobody"})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "user_not_found"


async def test_duplicate_is_409(client):
    await client.post("/api/accounts", json={"platform": "chesscom", "username": "hikaru"})
    r = await client.post("/api/accounts", json={"platform": "chesscom", "username": "Hikaru"})
    assert r.status_code == 409


async def test_bad_platform_is_400(client):
    r = await client.post("/api/accounts", json={"platform": "fics", "username": "x"})
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "validation_error"


async def test_sync_job_populates_games(client):
    acc = (
        await client.post("/api/accounts", json={"platform": "chesscom", "username": "hikaru"})
    ).json()
    r = await client.post(f"/api/accounts/{acc['id']}/sync", json={})
    assert r.status_code == 202
    job = r.json()
    assert job["kind"] == "sync" and job["account_id"] == acc["id"]
    final = await wait_for_job(client, job["id"])
    assert final["status"] == "done", final
    accounts = (await client.get("/api/accounts")).json()
    assert accounts[0]["game_count"] == 4
    assert accounts[0]["last_synced_at"] is not None


async def test_sync_all(client):
    a = (
        await client.post("/api/accounts", json={"platform": "chesscom", "username": "hikaru"})
    ).json()
    b = (
        await client.post(
            "/api/accounts", json={"platform": "lichess", "username": "DrNykterstein"}
        )
    ).json()
    r = await client.post("/api/accounts/sync-all")
    assert r.status_code == 202
    jobs = r.json()
    assert {j["account_id"] for j in jobs} == {a["id"], b["id"]}
    for j in jobs:
        assert (await wait_for_job(client, j["id"]))["status"] == "done"
    counts = {x["platform"]: x["game_count"] for x in (await client.get("/api/accounts")).json()}
    assert counts == {"chesscom": 4, "lichess": 3}


async def test_delete_cascades_games(client):
    acc = (
        await client.post("/api/accounts", json={"platform": "chesscom", "username": "hikaru"})
    ).json()
    job = (await client.post(f"/api/accounts/{acc['id']}/sync")).json()
    await wait_for_job(client, job["id"])
    assert (await client.get("/api/games")).json()["total"] == 4
    assert (await client.delete(f"/api/accounts/{acc['id']}")).status_code == 204
    assert (await client.get("/api/accounts")).json() == []
    assert (await client.get("/api/games")).json()["total"] == 0
