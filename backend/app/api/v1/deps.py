"""FastAPI Dependency Injection Helpers: DB Sessions, Authentication, and Role Guards."""

from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.security import decode_token
from backend.app.core.exceptions import AuthenticationException, PermissionDeniedException
from backend.app.db.session import get_db
from backend.app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """Extract and validate current authenticated user from Bearer token."""
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("Invalid token payload")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user


async def get_current_active_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Enforce Administrator role."""
    if current_user.role != UserRole.ADMIN and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required"
        )
    return current_user


async def get_current_risk_officer(
    current_user: User = Depends(get_current_user)
) -> User:
    """Enforce Lead Risk Officer or Admin role."""
    if current_user.role not in (UserRole.ADMIN, UserRole.RISK_LEAD) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Risk Officer privileges required"
        )
    return current_user
