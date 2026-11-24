from pydantic import BaseModel
from typing import List

class MarketplaceStats(BaseModel):
    total_providers: int
    online_providers: int
    total_available_ram_mb: float
    total_available_cpu_cores: int
    active_jobs: int
    completed_jobs: int

class AvailableResource(BaseModel):
    provider_id: str
    machine_name: str
    available_ram_mb: float
    available_cpu_percent: float
    os_type: str
    architecture: str
    reliability_score: float
    is_online: bool
    is_sharing: bool
    max_cpu_percent: float
    max_ram_mb: float
