import logging
from typing import Optional, List
from datetime import datetime, timezone
from app.storage.base import StorageBackend
from app.queue.base import QueueBackend
from app.models.provider import Provider
from app.models.job import Job, JobStatus

logger = logging.getLogger("ramshare.matchmaking")

class MatchmakingService:
    def __init__(self, storage: StorageBackend, queue: QueueBackend):
        self.storage = storage
        self.queue = queue

    def score_provider(self, provider: Provider, job: Job) -> float:
        # Constraint checks
        if not provider.is_online or not provider.is_sharing:
            return -1.0
        if provider.current_job_count >= provider.max_concurrent_jobs:
            return -1.0
        # Check RAM against max_ram_mb limit and current available
        effective_ram = min(provider.available_ram_mb, provider.max_ram_mb)
        if effective_ram < job.required_ram_mb:
            return -1.0

        # Weighted scoring: RAM (0.35), CPU (0.35), Reliability (0.15), Load availability (0.15)
        ram_score = min(1.0, effective_ram / (job.required_ram_mb * 2.0))
        cpu_score = min(1.0, provider.available_cpu_percent / 100.0)
        reliability_score = max(0.0, min(1.0, provider.reliability_score))
        load_score = 1.0 - (provider.current_job_count / max(1, provider.max_concurrent_jobs))

        total_score = (0.35 * ram_score) + (0.35 * cpu_score) + (0.15 * reliability_score) + (0.15 * load_score)
        return total_score

    async def find_best_provider(self, job: Job) -> Optional[Provider]:
        online_providers = await self.storage.list_providers(online_only=True)
        best_provider = None
        best_score = -1.0

        for provider in online_providers:
            score = self.score_provider(provider, job)
            if score > best_score:
                best_score = score
                best_provider = provider

        return best_provider

    async def reserve_provider(self, provider_id: str, job_id: str) -> bool:
        provider = await self.storage.get_provider_by_id(provider_id)
        if not provider:
            return False
        if provider.current_job_count >= provider.max_concurrent_jobs:
            return False
        await self.storage.update_provider(provider_id, current_job_count=provider.current_job_count + 1)
        return True

    async def release_provider(self, provider_id: str) -> None:
        provider = await self.storage.get_provider_by_id(provider_id)
        if provider and provider.current_job_count > 0:
            await self.storage.update_provider(provider_id, current_job_count=provider.current_job_count - 1)

    async def process_job_queue(self) -> int:
        messages = await self.queue.receive_messages(max_messages=10)
        processed = 0

        for msg in messages:
            job_id = msg["body"].get("job_id")
            receipt_handle = msg.get("receipt_handle")

            job = await self.storage.get_job_by_id(job_id)
            if not job:
                if receipt_handle:
                    await self.queue.delete_message(receipt_handle)
                continue

            if job.status not in (JobStatus.PENDING, JobStatus.QUEUED, JobStatus.MATCHING):
                if receipt_handle:
                    await self.queue.delete_message(receipt_handle)
                continue

            await self.storage.update_job(job_id, status=JobStatus.MATCHING)
            best_provider = await self.find_best_provider(job)

            if best_provider:
                reserved = await self.reserve_provider(best_provider.id, job.id)
                if reserved:
                    now_str = datetime.now(timezone.utc).isoformat()
                    await self.storage.update_job(
                        job_id,
                        provider_id=best_provider.id,
                        status=JobStatus.ASSIGNED,
                        started_at=now_str
                    )
                    if receipt_handle:
                        await self.queue.delete_message(receipt_handle)
                    processed += 1
                    logger.info(f"Matched job {job_id} to provider {best_provider.id}")
                else:
                    await self.storage.update_job(job_id, status=JobStatus.QUEUED)
            else:
                await self.storage.update_job(job_id, status=JobStatus.QUEUED)

        return processed
