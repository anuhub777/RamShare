import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from app.storage.base import StorageBackend
from app.queue.base import QueueBackend
from app.models.job import Job, JobStatus, WorkloadType
from app.schemas.job import JobSubmitRequest, JobStatusUpdate
from app.services.credit_service import CreditService
from app.config import settings

class JobService:
    def __init__(self, storage: StorageBackend, queue: QueueBackend):
        self.storage = storage
        self.queue = queue
        self.credit_service = CreditService(storage)

    async def submit_job(self, consumer_id: str, request: JobSubmitRequest) -> Job:
        user = await self.storage.get_user_by_id(consumer_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consumer not found")

        # Estimate credits
        estimated_credits = self.credit_service.calculate_cost(
            cpu_cores=request.required_cpu_cores,
            ram_mb=request.required_ram_mb,
            duration_seconds=request.max_execution_time
        )

        if user.credit_balance < estimated_credits:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits. Required: {estimated_credits}, Available: {user.credit_balance}"
            )

        job_id = uuid.uuid4().hex
        idempotency_key = f"job-{consumer_id}-{request.job_name}-{uuid.uuid4().hex[:8]}"

        job = Job(
            id=job_id,
            consumer_id=consumer_id,
            job_name=request.job_name,
            workload_type=request.workload_type,
            status=JobStatus.PENDING,
            required_ram_mb=request.required_ram_mb,
            required_cpu_cores=request.required_cpu_cores,
            max_execution_time=request.max_execution_time,
            input_params=request.input_params,
            estimated_credits=estimated_credits,
            idempotency_key=idempotency_key
        )
        created_job = await self.storage.create_job(job)

        # Enqueue for matchmaking
        await self.queue.send_message({"job_id": job_id})
        return created_job

    async def get_job(self, job_id: str, user_id: str) -> Job:
        job = await self.storage.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        # Verify access: consumer or assigned provider's user
        if job.consumer_id != user_id:
            if job.provider_id:
                provider = await self.storage.get_provider_by_id(job.provider_id)
                if not provider or provider.user_id != user_id:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return job

    async def list_jobs(self, user_id: str, status_filter: Optional[str] = None, limit: int = 50, offset: int = 0) -> Tuple[List[Job], int]:
        jobs = await self.storage.get_jobs_by_consumer(user_id, limit=limit, offset=offset)
        if status_filter:
            jobs = [j for j in jobs if j.status.value == status_filter]
        return jobs, len(jobs)

    async def cancel_job(self, job_id: str, consumer_id: str) -> Job:
        job = await self.storage.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        if job.consumer_id != consumer_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this job")
        if job.status not in (JobStatus.PENDING, JobStatus.QUEUED, JobStatus.MATCHING):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel job in state: {job.status.value}"
            )

        # Release provider if assigned
        if job.provider_id:
            provider = await self.storage.get_provider_by_id(job.provider_id)
            if provider and provider.current_job_count > 0:
                await self.storage.update_provider(job.provider_id, current_job_count=provider.current_job_count - 1)

        updated_job = await self.storage.update_job(job_id, status=JobStatus.CANCELLED)
        return updated_job

    async def update_job_status(self, job_id: str, provider_user_id: str, update: JobStatusUpdate) -> Job:
        job = await self.storage.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        # Verify provider ownership
        if not job.provider_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job has no provider assigned")

        provider = await self.storage.get_provider_by_id(job.provider_id)
        if not provider or provider.user_id != provider_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this job")

        now_str = datetime.now(timezone.utc).isoformat()
        update_kwargs = {"status": update.status}

        if update.status == JobStatus.RUNNING:
            if not job.started_at:
                update_kwargs["started_at"] = now_str

        elif update.status == JobStatus.COMPLETED:
            update_kwargs["completed_at"] = now_str
            update_kwargs["result_summary"] = update.result_summary
            update_kwargs["result_file_key"] = update.result_file_key
            credits_to_settle = update.actual_credits if update.actual_credits is not None else job.estimated_credits
            update_kwargs["actual_credits"] = credits_to_settle

            # Atomic credit transfer: Deduct consumer, award provider
            # Consumer deduction
            await self.credit_service.deduct_credits(
                user_id=job.consumer_id,
                job_id=job_id,
                amount=credits_to_settle,
                description=f"Job execution completed: {job.job_name}",
                idempotency_key=f"deduct-{job_id}"
            )

            # Provider reward (minus platform fee)
            reward = round(credits_to_settle * (1.0 - settings.platform_fee_percent / 100.0), 2)
            await self.credit_service.award_credits(
                user_id=provider.user_id,
                job_id=job_id,
                amount=reward,
                description=f"Reward for executing job: {job.job_name}",
                idempotency_key=f"reward-{job_id}"
            )

            # Release provider slot
            if provider.current_job_count > 0:
                await self.storage.update_provider(provider.id, current_job_count=provider.current_job_count - 1)

        elif update.status == JobStatus.FAILED:
            update_kwargs["completed_at"] = now_str
            update_kwargs["error_message"] = update.error_message

            # Check retry logic
            if job.retry_count < job.max_retries:
                update_kwargs["status"] = JobStatus.PENDING
                update_kwargs["retry_count"] = job.retry_count + 1
                update_kwargs["provider_id"] = None
                await self.queue.send_message({"job_id": job_id})
            else:
                # Refund consumer if any credits held
                pass

            # Release provider slot
            if provider.current_job_count > 0:
                await self.storage.update_provider(provider.id, current_job_count=provider.current_job_count - 1)

        return await self.storage.update_job(job_id, **update_kwargs)

    async def poll_jobs_for_provider(self, provider_id: str, provider_user_id: str) -> List[Job]:
        provider = await self.storage.get_provider_by_id(provider_id)
        if not provider or provider.user_id != provider_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        jobs = await self.storage.get_jobs_by_provider(provider_id)
        # Return assigned jobs ready to execute
        return [j for j in jobs if j.status == JobStatus.ASSIGNED]

    async def assign_job_to_provider(self, job_id: str, provider_id: str) -> Job:
        now_str = datetime.now(timezone.utc).isoformat()
        return await self.storage.update_job(
            job_id,
            provider_id=provider_id,
            status=JobStatus.ASSIGNED,
            started_at=now_str
        )
