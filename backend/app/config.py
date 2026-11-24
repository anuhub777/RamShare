import os
from typing import Literal
from pydantic import BaseModel, Field

def _resolve_default_db_path() -> str:
    env_path = os.getenv("RAMSHARE_DATABASE_URL")
    if env_path:
        return env_path
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(backend_dir, "ramshare.db")

class Settings(BaseModel):
    mode: Literal["local", "aws"] = Field(default_factory=lambda: os.getenv("RAMSHARE_MODE", "local"))
    backend_host: str = Field(default_factory=lambda: os.getenv("RAMSHARE_BACKEND_HOST", "0.0.0.0"))
    backend_port: int = Field(default_factory=lambda: int(os.getenv("RAMSHARE_BACKEND_PORT", "8000")))
    secret_key: str = Field(default_factory=lambda: os.getenv("RAMSHARE_SECRET_KEY", "ramshare-super-secret-key-change-in-production-2026"))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    debug: bool = True
    database_url: str = Field(default_factory=_resolve_default_db_path)

    # AWS settings (used when mode == "aws")
    aws_region: str = Field(default_factory=lambda: os.getenv("RAMSHARE_AWS_REGION", "us-east-1"))
    cognito_user_pool_id: str = Field(default_factory=lambda: os.getenv("RAMSHARE_COGNITO_USER_POOL_ID", ""))
    cognito_client_id: str = Field(default_factory=lambda: os.getenv("RAMSHARE_COGNITO_CLIENT_ID", ""))
    dynamodb_users_table: str = Field(default_factory=lambda: os.getenv("RAMSHARE_DYNAMODB_USERS_TABLE", "ramshare-users"))
    dynamodb_providers_table: str = Field(default_factory=lambda: os.getenv("RAMSHARE_DYNAMODB_PROVIDERS_TABLE", "ramshare-providers"))
    dynamodb_jobs_table: str = Field(default_factory=lambda: os.getenv("RAMSHARE_DYNAMODB_JOBS_TABLE", "ramshare-jobs"))
    dynamodb_credits_table: str = Field(default_factory=lambda: os.getenv("RAMSHARE_DYNAMODB_CREDITS_TABLE", "ramshare-credits"))
    sqs_job_queue_url: str = Field(default_factory=lambda: os.getenv("RAMSHARE_SQS_JOB_QUEUE_URL", ""))
    sqs_dlq_url: str = Field(default_factory=lambda: os.getenv("RAMSHARE_SQS_DLQ_URL", ""))
    s3_bucket: str = Field(default_factory=lambda: os.getenv("RAMSHARE_S3_BUCKET", "ramshare-storage"))

    # Provider agent settings
    provider_heartbeat_timeout: int = 60  # seconds before marked offline
    default_credits: float = 500.0

    # Pricing constants
    credit_per_cpu_minute: float = 1.0
    credit_per_gb_ram_minute: float = 0.5
    platform_fee_percent: float = 10.0

settings = Settings()
