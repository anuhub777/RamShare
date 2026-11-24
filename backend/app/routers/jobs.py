from typing import Optional, List
from fastapi import APIRouter, Depends, status
from app.schemas.job import JobSubmitRequest, JobStatusUpdate, JobResponse, JobListResponse
from app.services.job_service import JobService
from app.models.user import User
from app.dependencies import get_job_service, get_current_user

router = APIRouter()

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def submit_job(
    request: JobSubmitRequest,
    current_user: User = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    return await service.submit_job(current_user.id, request)

@router.get("", response_model=JobListResponse)
async def list_jobs(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    jobs, total = await service.list_jobs(current_user.id, status_filter=status, limit=limit, offset=offset)
    return JobListResponse(jobs=jobs, total=total)

@router.get("/poll/{provider_id}", response_model=List[JobResponse])
async def poll_jobs_for_provider(
    provider_id: str,
    current_user: User = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    return await service.poll_jobs_for_provider(provider_id, current_user.id)

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    return await service.get_job(job_id, current_user.id)

@router.post("/{job_id}/cancel", response_model=JobResponse)
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    return await service.cancel_job(job_id, current_user.id)

@router.post("/{job_id}/status", response_model=JobResponse)
async def update_job_status(
    job_id: str,
    request: JobStatusUpdate,
    current_user: User = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    return await service.update_job_status(job_id, current_user.id, request)

@router.get("/{job_id}/result")
async def get_job_result(
    job_id: str,
    current_user: User = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    job = await service.get_job(job_id, current_user.id)
    return {
        "job_id": job.id,
        "status": job.status,
        "result_summary": job.result_summary,
        "result_file_key": job.result_file_key,
        "actual_credits": job.actual_credits
    }
