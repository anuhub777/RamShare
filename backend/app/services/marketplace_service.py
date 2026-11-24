from typing import List
from app.storage.base import StorageBackend
from app.schemas.marketplace import MarketplaceStats, AvailableResource
from app.models.job import JobStatus

class MarketplaceService:
    def __init__(self, storage: StorageBackend):
        self.storage = storage

    async def get_statistics(self) -> MarketplaceStats:
        all_providers = await self.storage.list_providers(online_only=False)
        online_providers = [p for p in all_providers if p.is_online and p.is_sharing]

        total_ram = sum(p.available_ram_mb for p in online_providers)
        total_cores = sum(p.total_cpu_cores for p in online_providers)

        all_jobs = await self.storage.list_jobs(limit=1000)
        active_jobs = sum(1 for j in all_jobs if j.status in (JobStatus.QUEUED, JobStatus.MATCHING, JobStatus.ASSIGNED, JobStatus.RUNNING))
        completed_jobs = sum(1 for j in all_jobs if j.status == JobStatus.COMPLETED)

        return MarketplaceStats(
            total_providers=len(all_providers),
            online_providers=len(online_providers),
            total_available_ram_mb=round(total_ram, 1),
            total_available_cpu_cores=total_cores,
            active_jobs=active_jobs,
            completed_jobs=completed_jobs
        )

    async def get_available_resources(self) -> List[AvailableResource]:
        online = await self.storage.list_providers(online_only=True)
        return [
            AvailableResource(
                provider_id=p.id,
                machine_name=p.machine_name,
                available_ram_mb=p.available_ram_mb,
                available_cpu_percent=p.available_cpu_percent,
                os_type=p.os_type,
                architecture=p.architecture,
                reliability_score=p.reliability_score,
                is_online=p.is_online,
                is_sharing=p.is_sharing,
                max_cpu_percent=p.max_cpu_percent,
                max_ram_mb=p.max_ram_mb
            )
            for p in online
        ]
