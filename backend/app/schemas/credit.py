from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from app.models.credit import TransactionType

class CreditBalanceResponse(BaseModel):
    user_id: str
    balance: float

class CreditEstimateRequest(BaseModel):
    workload_type: str
    required_ram_mb: float = 512.0
    required_cpu_cores: int = 1
    estimated_duration_seconds: int = 60

class CreditEstimateResponse(BaseModel):
    estimated_credits: float
    breakdown: Dict[str, Any]

class TransactionResponse(BaseModel):
    id: str
    user_id: str
    job_id: Optional[str]
    transaction_type: TransactionType
    amount: float
    balance_after: float
    description: str
    created_at: str
    idempotency_key: Optional[str]

class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int
