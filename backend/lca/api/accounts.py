from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import Account, Game
from ..platforms.base import PlatformError
from ..services.jobs import job_to_dict
from .deps import get_session
from .errors import ApiError
from .schemas import AccountCreate, AccountOut, JobOut, SyncRequest

router = APIRouter(prefix="/accounts", tags=["accounts"])


async def _account_out(session: AsyncSession, account: Account) -> AccountOut:
    analyzed = await session.scalar(
        select(func.count())
        .select_from(Game)
        .where(Game.account_id == account.id, Game.analysis_status == "done")
    )
    return AccountOut(
        id=account.id,
        platform=account.platform,
        username=account.username,
        created_at=account.created_at,
        last_synced_at=account.last_synced_at,
        game_count=account.game_count,
        analyzed_count=int(analyzed or 0),
    )


async def _get_or_404(session: AsyncSession, account_id: int) -> Account:
    account = await session.get(Account, account_id)
    if account is None:
        raise ApiError(404, "not_found", "Account not found")
    return account


@router.get("", response_model=list[AccountOut])
async def list_accounts(session: AsyncSession = Depends(get_session)) -> list[AccountOut]:
    rows = (await session.execute(select(Account).order_by(Account.id))).scalars().all()
    return [await _account_out(session, a) for a in rows]


@router.post("", response_model=AccountOut, status_code=201)
async def create_account(
    body: AccountCreate, request: Request, session: AsyncSession = Depends(get_session)
) -> AccountOut:
    key = body.username.strip().lower()
    existing = await session.scalar(
        select(Account).where(Account.platform == body.platform, Account.username_key == key)
    )
    if existing is not None:
        raise ApiError(409, "already_linked", "That account is already linked")

    workers = request.app.state.workers
    settings = await request.app.state.settings.get_all()
    platform = workers.platform_factory(body.platform, settings)
    try:
        canonical = await platform.validate_user(body.username.strip())
    except PlatformError as e:
        raise ApiError(502, e.code, e.message) from e
    finally:
        aclose = getattr(platform, "aclose", None)
        if aclose is not None:
            await aclose()
    if canonical is None:
        raise ApiError(422, "user_not_found", f"No {body.platform} user named {body.username}")

    account = Account(platform=body.platform, username=canonical, username_key=key)
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return await _account_out(session, account)


@router.delete("/{account_id}", status_code=204)
async def delete_account(account_id: int, session: AsyncSession = Depends(get_session)) -> None:
    account = await _get_or_404(session, account_id)
    await session.delete(account)
    await session.commit()


@router.post("/{account_id}/sync", response_model=JobOut, status_code=202)
async def sync_account(
    account_id: int,
    request: Request,
    body: SyncRequest | None = None,
    session: AsyncSession = Depends(get_session),
) -> JobOut:
    await _get_or_404(session, account_id)
    months = body.months if body else None
    job = await request.app.state.workers.enqueue_sync(account_id, months)
    return JobOut(**job_to_dict(job))


@router.post("/sync-all", response_model=list[JobOut], status_code=202)
async def sync_all(request: Request, session: AsyncSession = Depends(get_session)) -> list[JobOut]:
    rows = (await session.execute(select(Account).order_by(Account.id))).scalars().all()
    jobs = [await request.app.state.workers.enqueue_sync(a.id) for a in rows]
    return [JobOut(**job_to_dict(j)) for j in jobs]
