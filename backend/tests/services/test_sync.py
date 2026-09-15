import pytest
from sqlalchemy import select

from lca.db.bootstrap import init_db
from lca.db.engine import make_engine, make_session_factory
from lca.db.models import Account, Game
from lca.platforms.base import PlatformError
from lca.services.sync import sync_account

from ..fakes import FakePlatform, chesscom_fixture_games


@pytest.fixture
async def sf(tmp_path):
    engine = make_engine(tmp_path / "t.db")
    await init_db(engine)
    factory = make_session_factory(engine)
    yield factory
    await engine.dispose()


async def _account(sf, username="Hikaru", platform="chesscom") -> int:
    async with sf() as s:
        acc = Account(platform=platform, username=username, username_key=username.lower())
        s.add(acc)
        await s.commit()
        return acc.id


async def test_sync_inserts_games_with_user_perspective(sf):
    account_id = await _account(sf)
    platform = FakePlatform("chesscom", chesscom_fixture_games(), {})
    progress = []

    async def on_progress(done, total, msg):
        progress.append((done, total, msg))

    result = await sync_account(sf, account_id, platform, on_progress=on_progress)
    assert result == {"fetched": 4, "created": 4}
    async with sf() as s:
        games = (await s.execute(select(Game).order_by(Game.played_at))).scalars().all()
        account = await s.get(Account, account_id)
    assert len(games) == 4
    first = games[0]
    assert first.black == "Hikaru" and first.user_color == "b"
    assert first.result == "1-0" and first.user_result == "loss"
    assert first.ply_count > 0
    assert first.analysis_status == "none"
    assert account.game_count == 4
    assert account.last_synced_at is not None
    assert account.sync_cursor == "c3"
    assert progress[-1][0] == progress[-1][1]


async def test_sync_is_idempotent(sf):
    account_id = await _account(sf)
    platform = FakePlatform("chesscom", chesscom_fixture_games(), {})
    await sync_account(sf, account_id, platform)
    again = await sync_account(sf, account_id, platform)
    assert again["created"] == 0
    async with sf() as s:
        assert len((await s.execute(select(Game))).scalars().all()) == 4


async def test_games_not_involving_user_are_skipped(sf):
    account_id = await _account(sf, username="someoneelse")
    platform = FakePlatform("chesscom", chesscom_fixture_games(), {})
    result = await sync_account(sf, account_id, platform)
    assert result["created"] == 0


async def test_new_games_are_offered_for_analysis(sf):
    account_id = await _account(sf)
    platform = FakePlatform("chesscom", chesscom_fixture_games(), {})
    enqueued = []

    async def enqueue(game_id):
        enqueued.append(game_id)

    await sync_account(sf, account_id, platform, enqueue_analyze=enqueue)
    assert len(enqueued) == 4


async def test_platform_errors_propagate(sf):
    account_id = await _account(sf)
    platform = FakePlatform("chesscom", chesscom_fixture_games(), {})
    platform.fail_with = PlatformError("upstream_error", "boom")
    with pytest.raises(PlatformError):
        await sync_account(sf, account_id, platform)
