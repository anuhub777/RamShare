from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime, timezone

class TransactionType(str, Enum):
    EARNING = "EARNING"
    SPENDING = "SPENDING"
    REFUND = "REFUND"
    SIGNUP_BONUS = "SIGNUP_BONUS"

class CreditTransaction(BaseModel):
    id: str
    user_id: str
    job_id: Optional[str] = None
    transaction_type: TransactionType
    amount: float
    balance_after: float
    description: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    idempotency_key: Optional[str] = None
