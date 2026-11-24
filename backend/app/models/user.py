from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timezone

class User(BaseModel):
    id: str
    username: str
    email: str
    hashed_password: str
    roles: List[str] = Field(default_factory=lambda: ["consumer"])
    credit_balance: float = 500.0
    is_active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
