import uuid
from fastapi import HTTPException, status
from app.storage.base import StorageBackend
from app.models.user import User
from app.models.credit import CreditTransaction, TransactionType
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.config import settings

class AuthService:
    def __init__(self, storage: StorageBackend):
        self.storage = storage

    async def register(self, request: RegisterRequest) -> TokenResponse:
        existing_user = await self.storage.get_user_by_username(request.username)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered")

        existing_email = await self.storage.get_user_by_email(request.email)
        if existing_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        user_id = uuid.uuid4().hex
        roles = request.roles or ["consumer"]
        initial_balance = settings.default_credits

        user = User(
            id=user_id,
            username=request.username,
            email=request.email,
            hashed_password=hash_password(request.password),
            roles=roles,
            credit_balance=initial_balance
        )
        await self.storage.create_user(user)

        # Signup bonus transaction
        bonus_txn = CreditTransaction(
            id=uuid.uuid4().hex,
            user_id=user_id,
            transaction_type=TransactionType.SIGNUP_BONUS,
            amount=initial_balance,
            balance_after=initial_balance,
            description="Welcome to RAMShare! Signup credit bonus",
            idempotency_key=f"signup-bonus-{user_id}"
        )
        await self.storage.create_transaction(bonus_txn)

        access_token = create_access_token(data={"sub": user.id, "username": user.username, "roles": user.roles})
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                roles=user.roles,
                credit_balance=user.credit_balance,
                created_at=user.created_at
            )
        )

    async def login(self, request: LoginRequest) -> TokenResponse:
        user = await self.storage.get_user_by_username(request.username)
        if not user or not verify_password(request.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

        access_token = create_access_token(data={"sub": user.id, "username": user.username, "roles": user.roles})
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                roles=user.roles,
                credit_balance=user.credit_balance,
                created_at=user.created_at
            )
        )

    async def get_user_by_id(self, user_id: str) -> User:
        user = await self.storage.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
