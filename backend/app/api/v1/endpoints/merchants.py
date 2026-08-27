"""Merchant Entity and Risk Management Endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.api.v1.deps import get_current_user, get_current_risk_officer
from backend.app.models.user import User
from backend.app.models.merchant import MerchantEntity
from backend.app.schemas.common import APIResponse

router = APIRouter()


@router.get("", summary="List Merchants")
async def list_merchants(
    category: Optional[str] = None,
    is_blacklisted: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List registered merchants with risk scores."""
    query = select(MerchantEntity)
    if category:
        query = query.where(MerchantEntity.category == category)
    if is_blacklisted is not None:
        query = query.where(MerchantEntity.is_blacklisted == is_blacklisted)

    result = await db.execute(query)
    merchants = result.scalars().all()
    return APIResponse(data=merchants)


@router.post("/{merchant_id}/blacklist", summary="Toggle Merchant Blacklist (Risk Officer only)")
async def toggle_merchant_blacklist(
    merchant_id: str,
    blacklist: bool = True,
    db: AsyncSession = Depends(get_db),
    officer: User = Depends(get_current_risk_officer)
):
    """Blacklist or un-blacklist merchant."""
    stmt = select(MerchantEntity).where(MerchantEntity.merchant_id == merchant_id)
    result = await db.execute(stmt)
    merchant = result.scalars().first()
    if not merchant:
        return APIResponse(success=False, message="Merchant not found", data=None)

    merchant.is_blacklisted = blacklist
    await db.commit()
    await db.refresh(merchant)
    return APIResponse(data=merchant, message=f"Merchant blacklist status set to {blacklist}")
