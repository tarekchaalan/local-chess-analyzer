async def test_defaults_and_update(client, app):
    r = await client.get("/api/settings")
    assert r.status_code == 200
    s = r.json()
    assert s["analysis_depth"] == "18" and s["theme"] == "system"
    assert s["setup_completed"] == "false"
    assert s["move_sounds"] == "true"

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


async def test_engine_path_empty_means_bundled(client, app):
    s = (await client.get("/api/settings")).json()
    assert s["engine_path"] == ""
    bundled = app.state.settings.bundled_engine_path()
    # saving the bundled path explicitly is normalised back to ""
    r = await client.patch("/api/settings", json={"engine_path": bundled})
    assert r.json()["settings"]["engine_path"] == ""
    assert await app.state.settings.engine_path() == bundled
    # a custom path that does not exist falls back to the bundled binary
    await client.patch("/api/settings", json={"engine_path": "/nope/stockfish"})
    assert await app.state.settings.engine_path() == bundled
    sysinfo = (await client.get("/api/system")).json()
    assert sysinfo["engine"]["custom_path"] == "/nope/stockfish"
    assert sysinfo["engine"]["is_bundled"] is True
