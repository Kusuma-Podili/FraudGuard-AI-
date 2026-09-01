"""Fraud Alert Management API Endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.api.v1.deps import get_current_user
from backend.app.models.user import User
from backend.app.schemas.alert import AlertResponse, AlertStatusUpdate, AlertAssignRequest, AlertCreate
from backend.app.schemas.case import CaseResponse
from backend.app.schemas.common import APIResponse, PaginatedResponse
from backend.app.services.alert_service import AlertService

router = APIRouter()


@router.get("", response_model=APIResponse[PaginatedResponse[AlertResponse]], summary="List Fraud Alerts")
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List fraud alerts with severity, status, and text search filters."""
    items, total = await AlertService.list_alerts(
        db=db,
        status=status,
        severity=severity,
        search=search,
        page=page,
        page_size=page_size
    )
    total_pages = (total + page_size - 1) // page_size
    paginated = PaginatedResponse[AlertResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return APIResponse(data=paginated)


@router.get("/{alert_id}", response_model=APIResponse[AlertResponse], summary="Get Alert Details")
async def get_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Retrieve single alert details by ID."""
    alert = await AlertService.get_alert_by_id(db, alert_id)
    return APIResponse(data=alert)


@router.patch("/{alert_id}/status", response_model=APIResponse[AlertResponse], summary="Update Alert Status")
async def update_alert_status(
    alert_id: str,
    update_in: AlertStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update alert status (e.g. to RESOLVED, FALSE_POSITIVE, ESCALATED)."""
    alert = await AlertService.update_alert_status(db, alert_id, update_in, user)
    return APIResponse(data=alert, message=f"Alert status updated to {update_in.status}")


@router.post("/{alert_id}/assign", response_model=APIResponse[AlertResponse], summary="Assign Alert")
async def assign_alert(
    alert_id: str,
    assign_in: AlertAssignRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Assign alert to a specific fraud analyst."""
    alert = await AlertService.assign_alert(db, alert_id, assign_in, user)
    return APIResponse(data=alert, message=f"Alert assigned to {assign_in.analyst_name}")


@router.post("/{alert_id}/convert-case", response_model=APIResponse[CaseResponse], status_code=status.HTTP_201_CREATED, summary="Convert Alert to Case")
async def convert_alert_to_case(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Escalate alert into an official investigation case."""
    alert, case = await AlertService.convert_to_case(db, alert_id, user)
    return APIResponse(data=case, message=f"Investigation case {case.case_number} created successfully")
