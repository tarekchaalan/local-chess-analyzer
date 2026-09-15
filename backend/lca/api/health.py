from fastapi import APIRouter

from .. import __version__
from .schemas import HealthOut

router = APIRouter()


@router.get("/health", response_model=HealthOut)
async def health() -> HealthOut:
    return HealthOut(ok=True, version=__version__)
