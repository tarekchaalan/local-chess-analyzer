async def test_system_info(client):
    r = await client.get("/api/system")
    assert r.status_code == 200
    body = r.json()
    assert body["cpu"]["logical_cores"] >= 1
    assert body["memory"]["recommended_hash_mb"] >= 128
    assert body["engine"]["valid"] is False  # no binary in the temp base dir
    assert body["recommended_depth"] in (15, 18, 20)


async def test_engine_validate_bogus_path(client, tmp_path):
    r = await client.post("/api/system/engine/validate", json={"path": str(tmp_path / "nope")})
    assert r.status_code == 200
    assert r.json()["valid"] is False and "exist" in r.json()["message"]
    bogus = tmp_path / "notanengine.sh"
    bogus.write_text("#!/bin/sh\necho hi\n")
    bogus.chmod(0o755)
    r = await client.post("/api/system/engine/validate", json={"path": str(bogus)})
    assert r.json()["valid"] is False
