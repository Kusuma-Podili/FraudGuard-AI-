"""Authentication and Identity Service."""

from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from backend.app.core.exceptions import AuthenticationException, EntityNotFoundException
from backend.app.models.user import User, UserRole
from backend.app.schemas.user import UserLoginRequest, UserCreateRequest, Token


class AuthService:
    """Handles user authentication, JWT lifecycle, and registrations."""

    @staticmethod
    async def authenticate_user(db: AsyncSession, creds: UserLoginRequest) -> Token:
        """Verify user credentials and issue signed JWTs."""
        stmt = select(User).where(User.email == creds.email)
        result = await db.execute(stmt)
        user = result.scalars().first()

        if not user or not verify_password(creds.password, user.hashed_password):
            raise AuthenticationException("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationException("Account is deactivated. Contact administrator.")

        # Update last login timestamp
        user.last_login_at = datetime.now(timezone.utc)
        await db.commit()

        access_token = create_access_token(subject=user.id, role=user.role.value)
        refresh_token = create_refresh_token(subject=user.id)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=86400,
            user_id=user.id,
            email=user.email,
            role=user.role.value,
            full_name=user.full_name,
        )

    @staticmethod
    async def create_user(db: AsyncSession, user_in: UserCreateRequest) -> User:
        """Register a new analyst or administrator user."""
        stmt = select(User).where(User.email == user_in.email)
        result = await db.execute(stmt)
        existing = result.scalars().first()
        if existing:
            raise AuthenticationException("Email is already registered.")

        role_enum = UserRole(user_in.role) if user_in.role in UserRole.__members__ else UserRole.FRAUD_ANALYST

        new_user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            role=role_enum,
            is_active=True,
            department=user_in.department or "Risk Operations",
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
