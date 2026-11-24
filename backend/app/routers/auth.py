from fastapi import APIRouter, Depends, status
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.models.user import User
from app.dependencies import get_auth_service, get_current_user

router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.register(request)

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.login(request)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        roles=current_user.roles,
        credit_balance=current_user.credit_balance,
        created_at=current_user.created_at
    )
