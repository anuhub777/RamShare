import threading
import time
import logging
import httpx
from typing import Optional
from agent.monitor import ResourceMonitor

logger = logging.getLogger("ramshare.agent.heartbeat")

class HeartbeatSender:
    def __init__(
        self,
        api_url: str,
        token: str,
        provider_id: str,
        monitor: ResourceMonitor,
        interval: int = 30,
        job_counter_callback = None
    ):
        self.api_url = api_url.rstrip("/")
        self.token = token
        self.provider_id = provider_id
        self.monitor = monitor
        self.interval = interval
        self.job_counter_callback = job_counter_callback
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run, daemon=True, name="HeartbeatThread")
            self._thread.start()
            logger.info(f"Heartbeat sender started (every {self.interval}s)")

    def stop(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        logger.info("Heartbeat sender stopped")

    def _run(self):
        while not self._stop_event.is_set():
            try:
                self.send_heartbeat()
            except Exception as e:
                logger.warning(f"Heartbeat error: {e}")
            self._stop_event.wait(self.interval)

    def send_heartbeat(self):
        resources = self.monitor.get_available_resources()
        active_jobs = self.job_counter_callback() if self.job_counter_callback else 0

        payload = {
            "provider_id": self.provider_id,
            "available_cpu_percent": resources["available_cpu_percent"],
            "available_ram_mb": resources["available_ram_mb"],
            "available_disk_gb": resources["available_disk_gb"],
            "current_job_count": active_jobs,
        }

        headers = {"Authorization": f"Bearer {self.token}"}
        with httpx.Client(timeout=8.0) as client:
            resp = client.post(f"{self.api_url}/providers/heartbeat", json=payload, headers=headers)
            if resp.status_code == 200:
                logger.debug(f"Heartbeat sent: {payload['available_ram_mb']}MB RAM free")
            else:
                logger.warning(f"Heartbeat rejected: {resp.status_code} {resp.text}")
