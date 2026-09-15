from __future__ import annotations

from fastapi import APIRouter, Request

from ..services.jobs import job_to_dict
from .errors import ApiError
from .schemas import CountOut, JobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobOut])
async def list_jobs(request: Request, status: str | None = None) -> list[JobOut]:
    jobs = await request.app.state.runner.list(status)
    return [JobOut(**job_to_dict(j)) for j in jobs]


@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: int, request: Request) -> JobOut:
    job = await request.app.state.runner.get(job_id)
    if job is None:
        raise ApiError(404, "not_found", "Job not found")
    return JobOut(**job_to_dict(job))


@router.post("/{job_id}/cancel", response_model=JobOut)
async def cancel_job(job_id: int, request: Request) -> JobOut:
    runner = request.app.state.runner
    if not await runner.cancel(job_id):
        job = await runner.get(job_id)
        if job is None:
            raise ApiError(404, "not_found", "Job not found")
        raise ApiError(409, "not_active", "Job is not queued or running")
    return JobOut(**job_to_dict(await runner.get(job_id)))


@router.post("/cancel-all", response_model=CountOut)
async def cancel_all(request: Request) -> CountOut:
    return CountOut(count=await request.app.state.runner.cancel_all())


@router.delete("/finished", response_model=CountOut)
async def clear_finished(request: Request) -> CountOut:
    return CountOut(count=await request.app.state.runner.clear_finished())
