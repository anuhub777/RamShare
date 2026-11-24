from fastapi import APIRouter, Depends, status
from app.schemas.provider import (
    ProviderRegisterRequest, ProviderUpdateResources, HeartbeatRequest,
    HeartbeatResponse, ProviderResponse, ProviderListResponse, AvailabilityUpdateRequest
)
from app.schemas.job import JobListResponse, JobResponse
from app.services.provider_service import ProviderService
from app.services.job_service import JobService
from app.models.user import User
from app.dependencies import get_provider_service, get_job_service, get_current_user

router = APIRouter()

@router.post("/register", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def register_provider(
    request: ProviderRegisterRequest,
    current_user: User = Depends(get_current_user),
    service: ProviderService = Depends(get_provider_service)
):
    provider = await service.register_provider(current_user.id, request)
    return provider

@router.get("", response_model=ProviderListResponse)
async def list_providers(
    online_only: bool = False,
    current_user: User = Depends(get_current_user),
    service: ProviderService = Depends(get_provider_service)
):
    providers = await service.list_providers(online_only=online_only)
    return ProviderListResponse(providers=providers, total=len(providers))

@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    provider_id: str,
    current_user: User = Depends(get_current_user),
    service: ProviderService = Depends(get_provider_service)
):
    return await service.get_provider(provider_id)

@router.post("/heartbeat", response_model=HeartbeatResponse)
async def heartbeat(
    request: HeartbeatRequest,
    current_user: User = Depends(get_current_user),
    service: ProviderService = Depends(get_provider_service)
):
    return await service.heartbeat(request)

@router.patch("/{provider_id}/availability", response_model=ProviderResponse)
async def set_availability(
    provider_id: str,
    request: AvailabilityUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: ProviderService = Depends(get_provider_service)
):
    return await service.set_availability(provider_id, current_user.id, request.is_sharing)

@router.patch("/{provider_id}/resources", response_model=ProviderResponse)
async def update_resources(
    provider_id: str,
    request: ProviderUpdateResources,
    current_user: User = Depends(get_current_user),
    service: ProviderService = Depends(get_provider_service)
):
    return await service.update_resources(provider_id, current_user.id, request)

@router.get("/{provider_id}/jobs", response_model=JobListResponse)
async def get_provider_jobs(
    provider_id: str,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
    provider_service: ProviderService = Depends(get_provider_service)
):
    provider = await provider_service.get_provider(provider_id)
    jobs = await job_service.poll_jobs_for_provider(provider_id, current_user.id)
    return JobListResponse(jobs=jobs, total=len(jobs))
