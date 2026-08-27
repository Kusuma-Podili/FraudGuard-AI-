"""Compliance Audit Logs API Endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.api.v1.deps import get_current_user
from backend.app.models.user import User
from backend.app.models.audit_log import AuditLogRecord
from backend.app.schemas.audit import AuditLogResponse
from backend.app.schemas.common import APIResponse, PaginatedResponse

router = APIRouter()


@router.get("", response_model=APIResponse[PaginatedResponse[AuditLogResponse]], summary="List Audit Logs")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    action_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Retrieve immutable audit logs for compliance auditing."""
    query = select(AuditLogRecord)
    count_query = select(func.count(AuditLogRecord.id))

    if action_type:
        query = query.where(AuditLogRecord.action_type == action_type)
        count_query = count_query.where(AuditLogRecord.action_type == action_type)

    total = (await db.execute(count_query)).scalar() or 0
    offset = (page - 1) * page_size
    query = query.order_by(desc(AuditLogRecord.created_at)).offset(offset).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()
    total_pages = (total + page_size - 1) // page_size

    paginated = PaginatedResponse[AuditLogResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return APIResponse(data=paginated)
