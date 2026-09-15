import sqlite3

from ..conftest import wait_for_job


async def _seed(client):
    acc = (
        await client.post("/api/accounts", json={"platform": "chesscom", "username": "hikaru"})
    ).json()
    job = (await client.post(f"/api/accounts/{acc['id']}/sync")).json()
    await wait_for_job(client, job["id"])


async def test_export_is_a_valid_snapshot(client, tmp_path):
    await _seed(client)
    r = await client.get("/api/database/export")
    assert r.status_code == 200
    assert r.headers["content-disposition"].startswith("attachment")
    out = tmp_path / "export.db"
    out.write_bytes(r.content)
    conn = sqlite3.connect(out)
    assert conn.execute("SELECT COUNT(*) FROM games").fetchone()[0] == 4
    conn.close()


async def test_import_rejects_garbage(client):
    r = await client.post(
        "/api/database/import",
        files={"file": ("x.db", b"not a database", "application/octet-stream")},
    )
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "invalid_database"


async def test_import_replaces_data(client, tmp_path):
    await _seed(client)
    exported = (await client.get("/api/database/export")).content
    reset = (await client.post("/api/database/reset")).json()
    assert reset["deleted_games"] == 4 and reset["deleted_accounts"] == 1
    assert (await client.get("/api/games")).json()["total"] == 0
    await client.patch("/api/settings", json={"theme": "dark"})

    r = await client.post(
        "/api/database/import", files={"file": ("backup.db", exported, "application/octet-stream")}
    )
    assert r.status_code == 200, r.text
    assert r.json()["games"] == 4 and r.json()["accounts"] == 1
    assert (await client.get("/api/games")).json()["total"] == 4
    assert (await client.get("/api/accounts")).json()[0]["username"] == "Hikaru"
    # settings come from the imported file (theme was still 'system' there)
    assert (await client.get("/api/settings")).json()["theme"] == "system"
