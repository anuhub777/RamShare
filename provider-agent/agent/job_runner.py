import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional
import httpx
from agent.docker_executor import DockerExecutor

logger = logging.getLogger("ramshare.agent.job_runner")

class JobRunner:
    def __init__(
        self,
        api_url: str,
        token: str,
        provider_id: str,
        executor: DockerExecutor,
        max_concurrent: int = 2,
        poll_interval: int = 5
    ):
        self.api_url = api_url.rstrip("/")
        self.token = token
        self.provider_id = provider_id
        self.executor = executor
        self.max_concurrent = max_concurrent
        self.poll_interval = poll_interval
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._pool = ThreadPoolExecutor(max_workers=max_concurrent)

        self.active_jobs: Dict[str, Dict[str, Any]] = {}
        self.completed_count = 0
        self.failed_count = 0
        self.earned_credits = 0.0

    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run, daemon=True, name="JobRunnerThread")
            self._thread.start()
            logger.info("Job runner started polling for assignments")

    def stop(self):
        self._stop_event.set()
        self._pool.shutdown(wait=False, cancel_futures=True)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        logger.info("Job runner stopped")

    def get_active_count(self) -> int:
        return len(self.active_jobs)

    def _run(self):
        while not self._stop_event.is_set():
            try:
                if len(self.active_jobs) < self.max_concurrent:
                    self._poll_and_dispatch()
            except Exception as e:
                logger.error(f"Error in job runner loop: {e}")
            self._stop_event.wait(self.poll_interval)

    def _poll_and_dispatch(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(f"{self.api_url}/jobs/poll/{self.provider_id}", headers=headers)
            if resp.status_code != 200:
                return
            jobs = resp.json()

        for job in jobs:
            job_id = job.get("id")
            if job_id and job_id not in self.active_jobs:
                if len(self.active_jobs) >= self.max_concurrent:
                    break
                self.active_jobs[job_id] = job
                logger.info(f"Accepted job: {job_id} ({job.get('job_name')})")
                self._pool.submit(self._execute_single_job, job)

    def _execute_single_job(self, job: Dict[str, Any]):
        job_id = job["id"]
        headers = {"Authorization": f"Bearer {self.token}"}

        # 1. Notify RUNNING
        try:
            with httpx.Client(timeout=8.0) as client:
                client.post(
                    f"{self.api_url}/jobs/{job_id}/status",
                    json={"status": "RUNNING"},
                    headers=headers
                )
        except Exception as e:
            logger.warning(f"Could not update job to RUNNING: {e}")

        # 2. Execute via Docker
        result = self.executor.execute_workload(job)

        # 3. Notify COMPLETED or FAILED
        try:
            with httpx.Client(timeout=10.0) as client:
                if result["success"]:
                    actual_credits = job.get("estimated_credits", 10.0)
                    resp = client.post(
                        f"{self.api_url}/jobs/{job_id}/status",
                        json={
                            "status": "COMPLETED",
                            "result_summary": result["output"][:2000],
                            "actual_credits": actual_credits
                        },
                        headers=headers
                    )
                    self.completed_count += 1
                    self.earned_credits += round(actual_credits * 0.9, 2)
                    logger.info(f"Job {job_id} COMPLETED successfully. Earned ~{round(actual_credits * 0.9, 2)} credits.")
                else:
                    client.post(
                        f"{self.api_url}/jobs/{job_id}/status",
                        json={
                            "status": "FAILED",
                            "error_message": result.get("error", "Unknown execution failure")
                        },
                        headers=headers
                    )
                    self.failed_count += 1
                    logger.warning(f"Job {job_id} FAILED: {result.get('error')}")
        except Exception as e:
            logger.error(f"Failed to post completion status for job {job_id}: {e}")
        finally:
            self.active_jobs.pop(job_id, None)
            self.executor.cleanup_job(job_id)
