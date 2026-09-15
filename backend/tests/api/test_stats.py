import pytest

from ..conftest import wait_for_job


@pytest.fixture
async def analyzed(client):
    acc = (
        await client.post("/api/accounts", json={"platform": "chesscom", "username": "hikaru"})
    ).json()
    job = (await client.post(f"/api/accounts/{acc['id']}/sync")).json()
    await wait_for_job(client, job["id"])
    ids = [g["id"] for g in (await client.get("/api/games")).json()["items"]]
    jobs = (await client.post("/api/games/analyze", json={"game_ids": ids[:2]})).json()["jobs"]
    for j in jobs:
        assert (await wait_for_job(client, j["id"], timeout=30))["status"] == "done"
    return acc


async def test_overview(client, analyzed):
    r = await client.get("/api/stats/overview")
    assert r.status_code == 200
    body = r.json()
    assert body["games"] == 4 and body["analyzed"] == 2 and body["accounts"] == 1
    assert body["wins"] + body["draws"] + body["losses"] == 4
    assert body["win_rate"] == 50.0
    assert 0 <= body["mean_accuracy"] <= 100
    assert (await client.get("/api/stats/overview", params={"account_id": 999})).json()[
        "games"
    ] == 0


async def test_accuracy_trend(client, analyzed):
    month = (await client.get("/api/stats/accuracy-trend")).json()
    assert len(month) == 1 and month[0]["bucket"] == "2025-08" and month[0]["games"] == 2
    week = (await client.get("/api/stats/accuracy-trend", params={"bucket": "week"})).json()
    assert len(week) == 1 and week[0]["bucket"].startswith("2025-W")


async def test_by_time_class(client, analyzed):
    rows = (await client.get("/api/stats/by-time-class")).json()
    assert len(rows) == 1
    row = rows[0]
    assert row["time_class"] == "rapid" and row["games"] == 4 and row["analyzed"] == 2
    assert row["blunders_per_game"] is not None and row["mistakes_per_game"] is not None


async def test_openings(client, analyzed):
    rows = (await client.get("/api/stats/openings")).json()
    assert rows and all(r["name"] for r in rows)
    assert sum(r["games"] for r in rows) == 4
    white_only = (await client.get("/api/stats/openings", params={"color": "w"})).json()
    assert sum(r["games"] for r in white_only) == 2


async def test_results_by_color(client, analyzed):
    body = (await client.get("/api/stats/results")).json()
    assert body["white"]["games"] == 2 and body["black"]["games"] == 2
    assert body["white"]["wins"] + body["black"]["wins"] == 2
