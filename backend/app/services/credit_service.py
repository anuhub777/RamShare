import uuid
from typing import List
from fastapi import HTTPException
from app.storage.base import StorageBackend
from app.models.credit import CreditTransaction, TransactionType
from app.schemas.credit import CreditEstimateRequest, CreditEstimateResponse
from app.config import settings

class CreditService:
    def __init__(self, storage: StorageBackend):
        self.storage = storage

    async def get_balance(self, user_id: str) -> float:
        user = await self.storage.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.credit_balance

    def calculate_cost(self, cpu_cores: int, ram_mb: float, duration_seconds: int) -> float:
        duration_minutes = max(1.0, duration_seconds / 60.0)
        cpu_cost = cpu_cores * settings.credit_per_cpu_minute * duration_minutes
        ram_gb = ram_mb / 1024.0
        ram_cost = ram_gb * settings.credit_per_gb_ram_minute * duration_minutes
        base_cost = cpu_cost + ram_cost
        total_cost = base_cost * (1.0 + settings.platform_fee_percent / 100.0)
        return round(max(1.0, total_cost), 2)

    async def estimate_cost(self, request: CreditEstimateRequest) -> CreditEstimateResponse:
        duration_minutes = max(1.0, request.estimated_duration_seconds / 60.0)
        cpu_cost = request.required_cpu_cores * settings.credit_per_cpu_minute * duration_minutes
        ram_gb = request.required_ram_mb / 1024.0
        ram_cost = ram_gb * settings.credit_per_gb_ram_minute * duration_minutes
        fee = (cpu_cost + ram_cost) * (settings.platform_fee_percent / 100.0)
        total = round(max(1.0, cpu_cost + ram_cost + fee), 2)

        return CreditEstimateResponse(
            estimated_credits=total,
            breakdown={
                "cpu_cost": round(cpu_cost, 2),
                "ram_cost": round(ram_cost, 2),
                "platform_fee": round(fee, 2),
                "duration_minutes": round(duration_minutes, 2),
                "total": total
            }
        )

    async def deduct_credits(self, user_id: str, job_id: str, amount: float, description: str, idempotency_key: str = None) -> CreditTransaction:
        if idempotency_key:
            existing = await self.storage.get_transaction_by_idempotency_key(idempotency_key)
            if existing:
                return existing

        user = await self.storage.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.credit_balance < amount:
            raise HTTPException(status_code=402, detail=f"Insufficient credits. Available: {user.credit_balance}, Required: {amount}")

        new_balance = round(user.credit_balance - amount, 2)
        await self.storage.update_user_balance(user_id, new_balance)

        txn = CreditTransaction(
            id=uuid.uuid4().hex,
            user_id=user_id,
            job_id=job_id,
            transaction_type=TransactionType.SPENDING,
            amount=amount,
            balance_after=new_balance,
            description=description,
            idempotency_key=idempotency_key
        )
        return await self.storage.create_transaction(txn)

    async def award_credits(self, user_id: str, job_id: str, amount: float, description: str, idempotency_key: str = None) -> CreditTransaction:
        if idempotency_key:
            existing = await self.storage.get_transaction_by_idempotency_key(idempotency_key)
            if existing:
                return existing

        user = await self.storage.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_balance = round(user.credit_balance + amount, 2)
        await self.storage.update_user_balance(user_id, new_balance)

        txn = CreditTransaction(
            id=uuid.uuid4().hex,
            user_id=user_id,
            job_id=job_id,
            transaction_type=TransactionType.EARNING,
            amount=amount,
            balance_after=new_balance,
            description=description,
            idempotency_key=idempotency_key
        )
        return await self.storage.create_transaction(txn)

    async def refund_credits(self, user_id: str, job_id: str, amount: float, description: str, idempotency_key: str = None) -> CreditTransaction:
        if idempotency_key:
            existing = await self.storage.get_transaction_by_idempotency_key(idempotency_key)
            if existing:
                return existing

        user = await self.storage.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_balance = round(user.credit_balance + amount, 2)
        await self.storage.update_user_balance(user_id, new_balance)

        txn = CreditTransaction(
            id=uuid.uuid4().hex,
            user_id=user_id,
            job_id=job_id,
            transaction_type=TransactionType.REFUND,
            amount=amount,
            balance_after=new_balance,
            description=description,
            idempotency_key=idempotency_key
        )
        return await self.storage.create_transaction(txn)

    async def get_transactions(self, user_id: str, limit: int = 50, offset: int = 0) -> List[CreditTransaction]:
        return await self.storage.get_transactions(user_id, limit, offset)
