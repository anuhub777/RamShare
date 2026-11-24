from fastapi import APIRouter, Depends
from app.schemas.credit import (
    CreditBalanceResponse, CreditEstimateRequest, CreditEstimateResponse,
    TransactionResponse, TransactionListResponse
)
from app.services.credit_service import CreditService
from app.models.user import User
from app.dependencies import get_credit_service, get_current_user

router = APIRouter()

@router.get("/balance", response_model=CreditBalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_user),
    service: CreditService = Depends(get_credit_service)
):
    balance = await service.get_balance(current_user.id)
    return CreditBalanceResponse(user_id=current_user.id, balance=balance)

@router.post("/estimate", response_model=CreditEstimateResponse)
async def estimate_credits(
    request: CreditEstimateRequest,
    current_user: User = Depends(get_current_user),
    service: CreditService = Depends(get_credit_service)
):
    return await service.estimate_cost(request)

@router.get("/transactions", response_model=TransactionListResponse)
async def list_transactions(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    service: CreditService = Depends(get_credit_service)
):
    txns = await service.get_transactions(current_user.id, limit=limit, offset=offset)
    return TransactionListResponse(
        transactions=[TransactionResponse(**t.model_dump()) for t in txns],
        total=len(txns)
    )
