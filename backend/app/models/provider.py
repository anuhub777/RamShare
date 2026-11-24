from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

class Provider(BaseModel):
    id: str
    user_id: str
    machine_name: str
    os_type: str
    os_version: str
    architecture: str
    total_cpu_cores: int
    total_ram_mb: float
    total_disk_gb: float
    available_cpu_percent: float = 0.0
    available_ram_mb: float = 0.0
    available_disk_gb: float = 0.0
    max_cpu_percent: float = 50.0
    max_ram_mb: float = 2048.0
    max_concurrent_jobs: int = 2
    current_job_count: int = 0
    is_online: bool = False
    is_sharing: bool = False
    last_heartbeat: Optional[str] = None
    registered_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reliability_score: float = 1.0
