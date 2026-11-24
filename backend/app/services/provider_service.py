import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from app.storage.base import StorageBackend
from app.models.provider import Provider
from app.schemas.provider import ProviderRegisterRequest, ProviderUpdateResources, HeartbeatRequest, HeartbeatResponse
from app.config import settings

class ProviderService:
    def __init__(self, storage: StorageBackend):
        self.storage = storage

    async def register_provider(self, user_id: str, request: ProviderRegisterRequest) -> Provider:
        user = await self.storage.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Upgrade roles to include provider
        if "provider" not in user.roles:
            new_roles = list(set(user.roles + ["provider"]))
            await self.storage.update_user(user_id, roles=new_roles)

        provider_id = uuid.uuid4().hex
        provider = Provider(
            id=provider_id,
            user_id=user_id,
            machine_name=request.machine_name,
            os_type=request.os_type,
            os_version=request.os_version,
            architecture=request.architecture,
            total_cpu_cores=request.total_cpu_cores,
            total_ram_mb=request.total_ram_mb,
            total_disk_gb=request.total_disk_gb,
            available_cpu_percent=100.0,
            available_ram_mb=request.total_ram_mb,
            available_disk_gb=request.total_disk_gb,
            max_cpu_percent=request.max_cpu_percent,
            max_ram_mb=request.max_ram_mb,
            max_concurrent_jobs=request.max_concurrent_jobs,
            is_online=True,
            is_sharing=True,
            last_heartbeat=datetime.now(timezone.utc).isoformat()
        )
        return await self.storage.create_provider(provider)

    async def get_provider(self, provider_id: str) -> Provider:
        provider = await self.storage.get_provider_by_id(provider_id)
        if not provider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
        return provider

    async def list_providers(self, online_only: bool = False) -> List[Provider]:
        return await self.storage.list_providers(online_only=online_only)

    async def heartbeat(self, request: HeartbeatRequest) -> HeartbeatResponse:
        provider = await self.storage.get_provider_by_id(request.provider_id)
        if not provider:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")

        now_str = datetime.now(timezone.utc).isoformat()
        await self.storage.update_provider(
            request.provider_id,
            available_cpu_percent=request.available_cpu_percent,
            available_ram_mb=request.available_ram_mb,
            available_disk_gb=request.available_disk_gb,
            current_job_count=request.current_job_count,
            is_online=True,
            last_heartbeat=now_str
        )
        return HeartbeatResponse(status="ok", provider_id=request.provider_id)

    async def set_availability(self, provider_id: str, user_id: str, is_sharing: bool) -> Provider:
        provider = await self.get_provider(provider_id)
        if provider.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this provider")

        updated = await self.storage.update_provider(provider_id, is_sharing=is_sharing)
        return updated

    async def update_resources(self, provider_id: str, user_id: str, request: ProviderUpdateResources) -> Provider:
        provider = await self.get_provider(provider_id)
        if provider.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this provider")

        update_kwargs = {
            "available_cpu_percent": request.available_cpu_percent,
            "available_ram_mb": request.available_ram_mb,
            "available_disk_gb": request.available_disk_gb,
        }
        if request.current_job_count is not None:
            update_kwargs["current_job_count"] = request.current_job_count

        return await self.storage.update_provider(provider_id, **update_kwargs)

    async def check_stale_providers(self) -> int:
        providers = await self.storage.list_providers(online_only=True)
        now = datetime.now(timezone.utc)
        timeout = timedelta(seconds=settings.provider_heartbeat_timeout)
        stale_count = 0

        for p in providers:
            if not p.last_heartbeat:
                await self.storage.update_provider(p.id, is_online=False)
                stale_count += 1
                continue
            try:
                hb_time = datetime.fromisoformat(p.last_heartbeat)
                if hb_time.tzinfo is None:
                    hb_time = hb_time.replace(tzinfo=timezone.utc)
                if now - hb_time > timeout:
                    await self.storage.update_provider(p.id, is_online=False)
                    stale_count += 1
            except Exception:
                await self.storage.update_provider(p.id, is_online=False)
                stale_count += 1

        return stale_count
