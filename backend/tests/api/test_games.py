import pytest

from ..conftest import wait_for_job, wait_until


@pytest.fixture
async def synced(client):
    acc = (
        await client.post("/api/accounts", json={"platform": "chesscom", "username": "hikaru"})
    ).json()
    job = (await client.post(f"/api/accounts/{acc['id']}/sync")).json()
    assert (await wait_for_job(client, job["id"]))["status"] == "done"
    return acc


async def test_list_default_sorted_newest_first(client, synced):
    r = await client.get("/api/games")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 4 and body["page"] == 1 and body["page_size"] == 25
    dates = [g["played_at"] for g in body["items"]]
    assert dates == sorted(dates, reverse=True)
    item = body["items"][0]
    assert "pgn" not in item
    assert item["opponent"] == "GHANDEEVAM2003"
    assert item["accuracy"] is None


async def test_filters(client, synced):
    assert (await client.get("/api/games", params={"user_result": "win"})).json()["total"] == 2
    assert (await client.get("/api/games", params={"color": "b"})).json()["total"] == 2
    assert (await client.get("/api/games", params={"time_class": "bullet"})).json()["total"] == 0
    assert (await client.get("/api/games", params={"search": "ghandee"})).json()["total"] == 4
    assert (await client.get("/api/games", params={"search": "zzz"})).json()["total"] == 0
    assert (
        await client.get("/api/games", params={"date_from": "2025-08-01", "date_to": "2025-08-01"})
    ).json()["total"] == 4
    assert (await client.get("/api/games", params={"date_to": "2025-07-31"})).json()["total"] == 0
    assert (await client.get("/api/games", params={"account_id": synced["id"]})).json()[
        "total"
    ] == 4
    assert (await client.get("/api/games", params={"account_id": 999})).json()["total"] == 0


async def test_pagination_and_validation(client, synced):
    r = await client.get("/api/games", params={"page": 2, "page_size": 3})
    assert r.json()["total"] == 4 and len(r.json()["items"]) == 1
    assert (await client.get("/api/games", params={"page_size": 0})).status_code == 400
    assert (await client.get("/api/games", params={"sort": "nope"})).status_code == 400
    assert (await client.get("/api/games", params={"date_from": "bad"})).status_code == 400


async def test_get_game_includes_pgn(client, synced):
    gid = (await client.get("/api/games")).json()["items"][0]["id"]
    r = await client.get(f"/api/games/{gid}")
    assert r.status_code == 200
    assert "[%clk" in r.json()["pgn"]
    assert r.json()["platform_accuracy_white"] is not None
    assert (await client.get("/api/games/9999")).status_code == 404


async def test_analyze_flow(client, synced):
    gid = (await client.get("/api/games")).json()["items"][0]["id"]
    assert (await client.get(f"/api/games/{gid}/analysis")).status_code == 404

    r = await client.post(f"/api/games/{gid}/analyze")
    assert r.status_code == 202
    job = r.json()
    assert job["kind"] == "analyze" and job["game_id"] == gid
    final = await wait_for_job(client, job["id"], timeout=15)
    assert final["status"] == "done", final
    assert final["progress"] == final["total"] > 0

    game = (await client.get(f"/api/games/{gid}")).json()
    assert game["analysis_status"] == "done"
    assert game["accuracy"] is not None

    analysis = (await client.get(f"/api/games/{gid}/analysis")).json()
    assert analysis["game_id"] == gid
    assert len(analysis["moves"]) == game["ply_count"]
    assert analysis["moves"][0]["classification"] in ("book", "best", "excellent", "good")
    assert analysis["opening_name"]
    assert set(analysis["counts"]) == {"w", "b"}

    # already analysed -> 409 unless force
    assert (await client.post(f"/api/games/{gid}/analyze")).status_code == 409
    r = await client.post(f"/api/games/{gid}/analyze", json={"force": True})
    assert r.status_code == 202
    assert (await wait_for_job(client, r.json()["id"], timeout=15))["status"] == "done"

    listed = (await client.get("/api/games", params={"sort": "accuracy"})).json()["items"]
    assert listed[0]["id"] == gid and listed[0]["accuracy"] is not None

    assert (await client.delete(f"/api/games/{gid}/analysis")).status_code == 204
    assert (await client.get(f"/api/games/{gid}")).json()["analysis_status"] == "none"
    assert (await client.get(f"/api/games/{gid}/analysis")).status_code == 404


async def test_bulk_analyze_skips_done_and_unknown(client, synced):
    ids = [g["id"] for g in (await client.get("/api/games")).json()["items"]]
    first = (await client.post(f"/api/games/{ids[0]}/analyze")).json()
    await wait_for_job(client, first["id"], timeout=15)
    r = await client.post("/api/games/analyze", json={"game_ids": ids + [9999]})
    assert r.status_code == 202
    body = r.json()
    assert sorted(body["skipped"]) == sorted([ids[0], 9999])
    assert {j["game_id"] for j in body["jobs"]} == set(ids[1:])
    for j in body["jobs"]:
        assert (await wait_for_job(client, j["id"], timeout=30))["status"] == "done"
    stats = (await client.get("/api/games", params={"analysis_status": "done"})).json()
    assert stats["total"] == 4


async def test_jobs_endpoints(client, synced):
    ids = [g["id"] for g in (await client.get("/api/games")).json()["items"]]
    r = await client.post("/api/games/analyze", json={"game_ids": ids})
    jobs = r.json()["jobs"]
    listed = (await client.get("/api/jobs")).json()
    assert {j["id"] for j in jobs} <= {j["id"] for j in listed}
    cancelled = (await client.post("/api/jobs/cancel-all")).json()["count"]
    assert cancelled >= 1

    async def all_finished():
        active = (await client.get("/api/jobs", params={"status": "active"})).json()
        return active == []

    assert await wait_until(all_finished, timeout=15)
    # cancelled-while-queued games are released, not left showing "queued"
    assert (await client.get("/api/games", params={"analysis_status": "queued"})).json()[
        "total"
    ] == 0
    cleared = (await client.delete("/api/jobs/finished")).json()["count"]
    assert cleared >= len(jobs)
    assert (await client.get("/api/jobs/123456")).status_code == 404


async def test_cancelled_reanalysis_keeps_existing_analysis(client, synced):
    gid = (await client.get("/api/games")).json()["items"][0]["id"]
    first = (await client.post(f"/api/games/{gid}/analyze")).json()
    assert (await wait_for_job(client, first["id"], timeout=15))["status"] == "done"

    # force a second run, then cancel everything before/while it runs
    job = (await client.post(f"/api/games/{gid}/analyze", json={"force": True})).json()
    await client.post("/api/jobs/cancel-all")
    final = await wait_for_job(client, job["id"], timeout=15)
    assert final["status"] in ("cancelled", "done")

    game = (await client.get(f"/api/games/{gid}")).json()
    assert game["analysis_status"] == "done"
    assert (await client.get(f"/api/games/{gid}/analysis")).status_code == 200


async def test_job_ids_are_never_reused(client, synced):
    ids = [g["id"] for g in (await client.get("/api/games")).json()["items"]]
    a = (await client.post(f"/api/games/{ids[0]}/analyze")).json()
    await wait_for_job(client, a["id"], timeout=15)
    await client.delete("/api/jobs/finished")
    b = (await client.post(f"/api/games/{ids[1]}/analyze")).json()
    assert b["id"] > a["id"]
