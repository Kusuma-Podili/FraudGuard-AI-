"""Customer & Card 360 Behavioral Investigation API Endpoints."""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.api.v1.deps import get_current_user
from backend.app.models.user import User
from backend.app.schemas.customer import CustomerProfileResponse, CustomerProfileUpdate
from backend.app.schemas.common import APIResponse, PaginatedResponse
from backend.app.services.customer_service import CustomerService

router = APIRouter()


@router.get("", response_model=APIResponse[PaginatedResponse[CustomerProfileResponse]], summary="List Customer Profiles")
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    risk_tier: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List customer/card profiles with risk tier and search filters."""
    items, total = await CustomerService.list_customers(
        db=db,
        search=search,
        risk_tier=risk_tier,
        page=page,
        page_size=page_size
    )
    total_pages = (total + page_size - 1) // page_size
    paginated = PaginatedResponse[CustomerProfileResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return APIResponse(data=paginated)


@router.get("/{identifier}/dossier", summary="Get Customer 360 Dossier")
async def get_customer_dossier(
    identifier: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Retrieve full customer 360 investigation dossier including transaction history and behavioral baseline."""
    dossier = await CustomerService.get_customer_dossier(db, identifier)
    return APIResponse(data=dossier)
