"""Authentication and User Management Endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.api.v1.deps import get_current_user, get_current_active_admin
from backend.app.models.user import User
from backend.app.schemas.user import UserLoginRequest, UserCreateRequest, UserResponse, Token
from backend.app.schemas.common import APIResponse
from backend.app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=Token, summary="User Login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """OAuth2 compatible token login, get an access token for future requests."""
    creds = UserLoginRequest(email=form_data.username, password=form_data.password)
    return await AuthService.authenticate_user(db, creds)


@router.post("/login/json", response_model=APIResponse[Token], summary="JSON Login")
async def login_json(
    creds: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate with standard JSON body."""
    token = await AuthService.authenticate_user(db, creds)
    return APIResponse(data=token, message="Authentication successful")


@router.get("/me", response_model=APIResponse[UserResponse], summary="Current User Details")
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user profile."""
    return APIResponse(data=current_user)


@router.post("/register", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED, summary="Create User (Admin only)")
async def create_user(
    user_in: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_active_admin)
):
    """Create new analyst or admin account."""
    new_user = await AuthService.create_user(db, user_in)
    return APIResponse(data=new_user, message="User created successfully")
