"""Admin User Management API Endpoints."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.api.v1.deps import get_current_active_admin, get_current_user
from backend.app.models.user import User, UserRole
from backend.app.models.audit_log import AuditLogRecord
from backend.app.schemas.user import UserCreateRequest, UserUpdateRequest, UserPasswordResetRequest, UserResponse
from backend.app.schemas.common import APIResponse
from backend.app.core.security import get_password_hash
from backend.app.core.exceptions import EntityNotFoundException, DuplicateEntityException

router = APIRouter()


@router.get("", response_model=APIResponse[List[UserResponse]], summary="List All Platform Users (Admin only)")
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_active_admin)
):
    """Retrieve list of all analysts and admin accounts."""
    stmt = select(User).order_by(desc(User.created_at))
    res = await db.execute(stmt)
    users = res.scalars().all()
    return APIResponse(data=users)


@router.post("", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED, summary="Add User (Admin only)")
async def create_user(
    user_in: UserCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_active_admin)
):
    """Create a new fraud analyst or admin account."""
    stmt = select(User).where(User.email == user_in.email)
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        raise DuplicateEntityException(f"User with email {user_in.email} already exists")

    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=UserRole(user_in.role) if user_in.role in ("ADMIN", "FRAUD_ANALYST", "RISK_LEAD") else UserRole.FRAUD_ANALYST,
        department=user_in.department,
        is_active=True,
        is_superuser=(user_in.role == "ADMIN")
    )
    db.add(new_user)

    audit_log = AuditLogRecord(
        id=str(uuid.uuid4()),
        user_id=admin.id,
        user_email=admin.email,
        action_type="USER_CREATED",
        resource_type="USER",
        resource_id=user_in.email,
        change_summary=f"Created user account {user_in.email} with role {user_in.role}",
        ip_address="127.0.0.1",
        after_state={"role": user_in.role, "full_name": user_in.full_name}
    )
    db.add(audit_log)
    await db.commit()
    await db.refresh(new_user)
    return APIResponse(data=new_user, message="User created successfully")


@router.patch("/{user_id}", response_model=APIResponse[UserResponse], summary="Update User Details / Role (Admin only)")
async def update_user(
    user_id: str,
    update_in: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_active_admin)
):
    """Update user role, department, or active status."""
    stmt = select(User).where(User.id == user_id)
    target = (await db.execute(stmt)).scalars().first()
    if not target:
        raise EntityNotFoundException(f"User {user_id} not found")

    before_state = {
        "full_name": target.full_name,
        "role": target.role.value if hasattr(target.role, 'value') else str(target.role),
        "department": target.department,
        "is_active": target.is_active
    }

    if update_in.full_name is not None:
        target.full_name = update_in.full_name
    if update_in.role is not None:
        target.role = UserRole(update_in.role)
        target.is_superuser = (update_in.role == "ADMIN")
    if update_in.department is not None:
        target.department = update_in.department
    if update_in.is_active is not None:
        target.is_active = update_in.is_active

    audit_log = AuditLogRecord(
        id=str(uuid.uuid4()),
        user_id=admin.id,
        user_email=admin.email,
        action_type="USER_UPDATED",
        resource_type="USER",
        resource_id=target.email,
        change_summary=f"Updated profile/permissions for user {target.email}",
        ip_address="127.0.0.1",
        before_state=before_state,
        after_state=update_in.model_dump(exclude_unset=True)
    )
    db.add(audit_log)
    await db.commit()
    await db.refresh(target)
    return APIResponse(data=target, message="User updated successfully")


@router.post("/{user_id}/reset-password", response_model=APIResponse[dict], summary="Reset User Password (Admin only)")
async def reset_password(
    user_id: str,
    req: UserPasswordResetRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_active_admin)
):
    """Securely reset password for an analyst account."""
    stmt = select(User).where(User.id == user_id)
    target = (await db.execute(stmt)).scalars().first()
    if not target:
        raise EntityNotFoundException(f"User {user_id} not found")

    target.hashed_password = get_password_hash(req.new_password)

    audit_log = AuditLogRecord(
        id=str(uuid.uuid4()),
        user_id=admin.id,
        user_email=admin.email,
        action_type="USER_PASSWORD_RESET",
        resource_type="USER",
        resource_id=target.email,
        change_summary=f"Password reset triggered for user {target.email}",
        ip_address="127.0.0.1",
        after_state={"target_email": target.email}
    )
    db.add(audit_log)
    await db.commit()
    return APIResponse(data={"success": True}, message="Password reset successfully")
