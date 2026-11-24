import os
from pydantic import BaseModel, Field

class AgentConfig(BaseModel):
    api_url: str = Field(default_factory=lambda: os.getenv("RAMSHARE_AGENT_API_URL", "http://localhost:8000"))
    heartbeat_interval: int = Field(default_factory=lambda: int(os.getenv("RAMSHARE_AGENT_HEARTBEAT_INTERVAL", "30")))
    job_poll_interval: int = Field(default_factory=lambda: int(os.getenv("RAMSHARE_AGENT_JOB_POLL_INTERVAL", "5")))
    max_cpu_percent: float = Field(default_factory=lambda: float(os.getenv("RAMSHARE_AGENT_MAX_CPU_PERCENT", "50.0")))
    max_ram_mb: float = Field(default_factory=lambda: float(os.getenv("RAMSHARE_AGENT_MAX_RAM_MB", "2048.0")))
    max_concurrent_jobs: int = Field(default_factory=lambda: int(os.getenv("RAMSHARE_AGENT_MAX_CONCURRENT_JOBS", "2")))
    auto_pause_threshold: float = Field(default_factory=lambda: float(os.getenv("RAMSHARE_AGENT_AUTO_PAUSE_THRESHOLD", "85.0")))
    workload_timeout: int = Field(default_factory=lambda: int(os.getenv("RAMSHARE_AGENT_WORKLOAD_TIMEOUT", "300")))
    storage_dir: str = Field(default_factory=lambda: os.getenv("RAMSHARE_AGENT_STORAGE_DIR", "/tmp/ramshare-workloads"))

config = AgentConfig()
