import asyncio
from app.models.job import Job, WorkloadType, JobStatus
from app.models.provider import Provider
from app.services.matchmaking_service import MatchmakingService
from app.queue.local import LocalQueue

def test_matchmaking_selects_best_provider(storage):
    queue = LocalQueue()
    matchmaking = MatchmakingService(storage, queue)

    async def _run():
        # Provider A: Low RAM
        p1 = Provider(
            id="prov-a", user_id="u1", machine_name="Rig-Low", os_type="Linux",
            os_version="6.1", architecture="x86_64", total_cpu_cores=4, total_ram_mb=4096,
            total_disk_gb=100, available_cpu_percent=50, available_ram_mb=500,
            max_cpu_percent=50, max_ram_mb=1024, max_concurrent_jobs=2, current_job_count=0,
            is_online=True, is_sharing=True, reliability_score=0.9
        )
        # Provider B: High RAM, high availability
        p2 = Provider(
            id="prov-b", user_id="u2", machine_name="Rig-High", os_type="Linux",
            os_version="6.1", architecture="x86_64", total_cpu_cores=8, total_ram_mb=16384,
            total_disk_gb=500, available_cpu_percent=90, available_ram_mb=8000,
            max_cpu_percent=80, max_ram_mb=8000, max_concurrent_jobs=2, current_job_count=0,
            is_online=True, is_sharing=True, reliability_score=1.0
        )
        await storage.create_provider(p1)
        await storage.create_provider(p2)

        job = Job(
            id="job-1", consumer_id="consumer-1", job_name="ML Workload",
            workload_type=WorkloadType.ML_INFERENCE, required_ram_mb=2048, required_cpu_cores=2
        )

        best = await matchmaking.find_best_provider(job)
        return best

    best = asyncio.run(_run())
    assert best is not None
    assert best.id == "prov-b"
