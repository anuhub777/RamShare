import logging
import httpx
from typing import Dict, Any

logger = logging.getLogger("ramshare.agent.uploader")

class ResultUploader:
    def __init__(self, api_url: str, token: str):
        self.api_url = api_url.rstrip("/")
        self.token = token

    def upload_result(self, job_id: str, payload: Dict[str, Any], max_retries: int = 3) -> bool:
        headers = {"Authorization": f"Bearer {self.token}"}
        for attempt in range(1, max_retries + 1):
            try:
                with httpx.Client(timeout=15.0) as client:
                    resp = client.post(f"{self.api_url}/jobs/{job_id}/status", json=payload, headers=headers)
                    if resp.status_code == 200:
                        return True
            except Exception as e:
                logger.warning(f"Result upload attempt {attempt} failed: {e}")
        return False
