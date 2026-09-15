from __future__ import annotations

from fastapi import APIRouter, Depends

from ..services.settings import SettingsService
from ..services.system import system_info, validate_engine
from .deps import get_settings
from .schemas import EngineInfo, EngineValidateRequest, SystemOut

router = APIRouter(prefix="/system", tags=["system"])


@router.get("", response_model=SystemOut)
async def get_system(settings: SettingsService = Depends(get_settings)) -> SystemOut:
    return await system_info(await settings.get("engine_path"))


@router.post("/engine/validate", response_model=EngineInfo)
async def engine_validate(body: EngineValidateRequest) -> EngineInfo:
    return await validate_engine(body.path)
