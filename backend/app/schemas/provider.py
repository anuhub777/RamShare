from pydantic import BaseModel, Field
from typing import Optional, List

class ProviderRegisterRequest(BaseModel):
    machine_name: str
    os_type: str
    os_version: str
    architecture: str
    total_cpu_cores: int
    total_ram_mb: float
    total_disk_gb: float
    max_cpu_percent: float = Field(default=50.0, ge=1.0, le=100.0)
    max_ram_mb: float = Field(default=2048.0, ge=256.0)
    max_concurrent_jobs: int = Field(default=2, ge=1, le=16)

class ProviderUpdateResources(BaseModel):
    available_cpu_percent: float
    available_ram_mb: float
    available_disk_gb: float
    current_job_count: Optional[int] = None

class HeartbeatRequest(BaseModel):
    provider_id: str
    available_cpu_percent: float
    available_ram_mb: float
    available_disk_gb: float
    current_job_count: int = 0

class HeartbeatResponse(BaseModel):
    status: str = "ok"
    provider_id: str

class ProviderResponse(BaseModel):
    id: str
    user_id: str
    machine_name: str
    os_type: str
    os_version: str
    architecture: str
    total_cpu_cores: int
    total_ram_mb: float
    total_disk_gb: float
    available_cpu_percent: float
    available_ram_mb: float
    available_disk_gb: float
    max_cpu_percent: float
    max_ram_mb: float
    max_concurrent_jobs: int
    current_job_count: int
    is_online: bool
    is_sharing: bool
    last_heartbeat: Optional[str]
    registered_at: str
    reliability_score: float

class ProviderListResponse(BaseModel):
    providers: List[ProviderResponse]
    total: int

class AvailabilityUpdateRequest(BaseModel):
    is_sharing: bool
