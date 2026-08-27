"""Investigation Case Management and Analyst Action Endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.api.v1.deps import get_current_user
from backend.app.models.user import User
from backend.app.schemas.case import CaseResponse, CaseStatusUpdate, CaseAssignRequest, CaseNoteCreate, CaseNoteResponse
from backend.app.schemas.common import APIResponse, PaginatedResponse
from backend.app.services.case_service import CaseService

router = APIRouter()


@router.get("", response_model=APIResponse[PaginatedResponse[CaseResponse]], summary="List Investigation Cases")
async def list_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    assigned_to_me: Optional[bool] = False,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Retrieve case queue with status and severity filters."""
    assigned_filter = user.id if assigned_to_me else None
    items, total = await CaseService.list_cases(
        db=db,
        status=status,
        severity=severity,
        assigned_to_me=assigned_filter,
        page=page,
        page_size=page_size
    )

    total_pages = (total + page_size - 1) // page_size
    paginated = PaginatedResponse[CaseResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return APIResponse(data=paginated)


@router.get("/{case_id}", response_model=APIResponse[CaseResponse], summary="Get Case Details")
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Retrieve case dossier including evidence and notes."""
    case = await CaseService.get_case_by_id(db, case_id)
    return APIResponse(data=case)


@router.patch("/{case_id}/status", response_model=APIResponse[CaseResponse], summary="Update Case Status")
async def update_case_status(
    case_id: str,
    status_update: CaseStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Transition case status (e.g. to CONFIRMED_FRAUD or RESOLVED)."""
    case = await CaseService.update_status(db, case_id, status_update, user)
    return APIResponse(data=case, message=f"Case status transitioned to {status_update.status}")


@router.post("/{case_id}/assign", response_model=APIResponse[CaseResponse], summary="Assign Analyst")
async def assign_case(
    case_id: str,
    assignment: CaseAssignRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Assign an investigation case to a specific analyst."""
    case = await CaseService.assign_analyst(db, case_id, assignment, user)
    return APIResponse(data=case, message=f"Case assigned to {assignment.analyst_name}")


@router.post("/{case_id}/notes", response_model=APIResponse[CaseNoteResponse], status_code=status.HTTP_201_CREATED, summary="Add Case Note")
async def add_case_note(
    case_id: str,
    note_in: CaseNoteCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Append investigation note or evidence summary."""
    note = await CaseService.add_note(db, case_id, note_in, user)
    return APIResponse(data=note, message="Note added successfully")
