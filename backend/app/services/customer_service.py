"""Customer & Card 360 Behavioral Profiling Service."""

import uuid
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.customer import CustomerProfile
from backend.app.models.transaction import TransactionRecord
from backend.app.models.alert import AlertRecord
from backend.app.models.case import InvestigationCase
from backend.app.core.exceptions import EntityNotFoundException


class CustomerService:

    @staticmethod
    async def list_customers(
        db: AsyncSession,
        search: Optional[str] = None,
        risk_tier: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[CustomerProfile], int]:
        """List customer/card profiles with search and risk filters."""
        query = select(CustomerProfile)
        count_query = select(func.count(CustomerProfile.id))

        if risk_tier and risk_tier != "ALL":
            query = query.where(CustomerProfile.risk_tier == risk_tier)
            count_query = count_query.where(CustomerProfile.risk_tier == risk_tier)

        if search:
            pattern = f"%{search}%"
            filter_cond = (
                CustomerProfile.customer_id.ilike(pattern) |
                CustomerProfile.card_id.ilike(pattern) |
                CustomerProfile.masked_card.ilike(pattern) |
                CustomerProfile.full_name.ilike(pattern) |
                CustomerProfile.email.ilike(pattern)
            )
            query = query.where(filter_cond)
            count_query = count_query.where(filter_cond)

        total = (await db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = query.order_by(desc(CustomerProfile.created_at)).offset(offset).limit(page_size)

        res = await db.execute(query)
        return res.scalars().all(), total

    @staticmethod
    async def get_customer_by_card_or_id(db: AsyncSession, identifier: str) -> CustomerProfile:
        """Get customer profile by customer_id, card_id, or primary key."""
        stmt = select(CustomerProfile).where(
            (CustomerProfile.id == identifier) |
            (CustomerProfile.customer_id == identifier) |
            (CustomerProfile.card_id == identifier)
        )
        res = await db.execute(stmt)
        profile = res.scalars().first()
        if not profile:
            raise EntityNotFoundException(f"Customer/Card profile for {identifier} not found")
        return profile

    @staticmethod
    async def get_customer_dossier(db: AsyncSession, identifier: str) -> Dict[str, Any]:
        """Get 360 customer dossier including transaction history, alerts, cases, and baseline metrics."""
        profile = await CustomerService.get_customer_by_card_or_id(db, identifier)

        # 1. Fetch recent transactions for this card
        tx_stmt = select(TransactionRecord).where(
            TransactionRecord.card_id == profile.card_id
        ).order_by(desc(TransactionRecord.created_at)).limit(15)
        tx_res = await db.execute(tx_stmt)
        transactions = tx_res.scalars().all()

        # 2. Fetch alerts for this card
        alt_stmt = select(AlertRecord).where(
            AlertRecord.card_id == profile.card_id
        ).order_by(desc(AlertRecord.created_at)).limit(10)
        alt_res = await db.execute(alt_stmt)
        alerts = alt_res.scalars().all()

        # 3. Fetch cases for this card
        case_stmt = select(InvestigationCase).where(
            InvestigationCase.card_id == profile.card_id
        ).order_by(desc(InvestigationCase.created_at)).limit(5)
        case_res = await db.execute(case_stmt)
        cases = case_res.scalars().all()

        return {
            "profile": profile,
            "recent_transactions": transactions,
            "recent_alerts": alerts,
            "recent_cases": cases,
            "behavioral_baseline": {
                "avg_amount_30d": profile.avg_amount_30d,
                "max_amount_single": profile.max_amount_single,
                "typical_categories": profile.typical_categories or ["GROCERY", "RESTAURANT"],
                "typical_locations": profile.typical_locations or ["New York, US"],
                "known_devices": profile.known_devices or ["dev_apple_safari_1"],
                "total_transactions": profile.total_transactions_count,
                "total_alerts": profile.total_fraud_alerts_count,
                "total_cases": profile.total_cases_count,
            }
        }
