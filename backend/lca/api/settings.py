from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from ..services.settings import ENGINE_KEYS, SettingsService, SettingsValidationError
from .deps import get_settings
from .errors import ApiError
from .schemas import SettingsUpdateOut

router = APIRouter(prefix="/settings", tags=["settings"])

ANALYSIS_KEYS = frozenset({"analysis_depth", "analysis_time_ms"})


@router.get("", response_model=dict[str, str])
async def read_settings(settings: SettingsService = Depends(get_settings)) -> dict[str, str]:
    return await settings.get_all()


@router.patch("", response_model=SettingsUpdateOut)
async def update_settings(
    body: dict[str, object], request: Request, settings: SettingsService = Depends(get_settings)
) -> SettingsUpdateOut:
    try:
        updated = await settings.update(body)
    except SettingsValidationError as e:
        raise ApiError(400, "validation_error", "Invalid settings", e.errors) from e
    changed = set(updated)
    if changed & (ENGINE_KEYS | ANALYSIS_KEYS):
        await request.app.state.engines.invalidate(changed)
    return SettingsUpdateOut(updated=updated, settings=await settings.get_all())
