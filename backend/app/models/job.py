from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime, timezone

class WorkloadType(str, Enum):
    CPU_BENCHMARK = "CPU_BENCHMARK"
    MEMORY_BENCHMARK = "MEMORY_BENCHMARK"
    DATA_PROCESSING = "DATA_PROCESSING"
    ML_INFERENCE = "ML_INFERENCE"

class JobStatus(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    MATCHING = "MATCHING"
    ASSIGNED = "ASSIGNED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"

class Job(BaseModel):
    id: str
    consumer_id: str
    provider_id: Optional[str] = None
    job_name: str
    workload_type: WorkloadType
    status: JobStatus = JobStatus.PENDING
    required_ram_mb: float
    required_cpu_cores: int = 1
    max_execution_time: int = 300
    input_params: Dict[str, Any] = Field(default_factory=dict)
    input_file_key: Optional[str] = None
    result_file_key: Optional[str] = None
    result_summary: Optional[str] = None
    estimated_credits: float = 0.0
    actual_credits: Optional[float] = None
    idempotency_key: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 2
