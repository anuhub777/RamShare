from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from app.models.job import WorkloadType, JobStatus

class JobSubmitRequest(BaseModel):
    job_name: str = Field(..., min_length=2, max_length=100)
    workload_type: WorkloadType
    required_ram_mb: float = Field(default=512.0, ge=128.0)
    required_cpu_cores: int = Field(default=1, ge=1, le=16)
    max_execution_time: int = Field(default=300, ge=10, le=3600)
    input_params: Dict[str, Any] = Field(default_factory=dict)

class JobStatusUpdate(BaseModel):
    status: JobStatus
    result_summary: Optional[str] = None
    error_message: Optional[str] = None
    result_file_key: Optional[str] = None
    actual_credits: Optional[float] = None

class JobResponse(BaseModel):
    id: str
    consumer_id: str
    provider_id: Optional[str] = None
    job_name: str
    workload_type: WorkloadType
    status: JobStatus
    required_ram_mb: float
    required_cpu_cores: int
    max_execution_time: int
    input_params: Dict[str, Any]
    input_file_key: Optional[str] = None
    result_file_key: Optional[str] = None
    result_summary: Optional[str] = None
    estimated_credits: float
    actual_credits: Optional[float] = None
    idempotency_key: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 2

class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
