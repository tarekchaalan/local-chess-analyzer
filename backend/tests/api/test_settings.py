async def test_defaults_and_update(client, app):
    r = await client.get("/api/settings")
    assert r.status_code == 200
    s = r.json()
    assert s["analysis_depth"] == "18" and s["theme"] == "system"
    assert s["setup_completed"] == "false"

    r = await client.patch("/api/settings", json={"analysis_depth": 12, "theme": "dark"})
    assert r.status_code == 200
    assert sorted(r.json()["updated"]) == ["analysis_depth", "theme"]
    assert r.json()["settings"]["analysis_depth"] == "12"
    assert (await client.get("/api/settings")).json()["theme"] == "dark"


async def test_validation_errors(client):
    r = await client.patch("/api/settings", json={"engine_threads": 0, "theme": "neon", "nope": 1})
    assert r.status_code == 400
    err = r.json()["error"]
    assert err["code"] == "validation_error"
    assert set(err["details"]) == {"engine_threads", "theme", "nope"}


async def test_engine_settings_invalidate_session(client, app):
    await client.patch("/api/settings", json={"engine_threads": 2})
    assert app.state.engines.invalidated[-1] == {"engine_threads"}
    await client.patch("/api/settings", json={"analysis_time_ms": 500})
    assert app.state.engines.invalidated[-1] == {"analysis_time_ms"}
    n = len(app.state.engines.invalidated)
    await client.patch("/api/settings", json={"theme": "light"})
    assert len(app.state.engines.invalidated) == n
