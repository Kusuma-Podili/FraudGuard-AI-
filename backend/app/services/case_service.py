"""Investigation Case Management and Lifecycle Orchestrator Service."""

import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.case import InvestigationCase, CaseNote, CaseStatus, CaseSeverity
from backend.app.models.user import User
from backend.app.core.exceptions import EntityNotFoundException
from backend.app.schemas.case import CaseStatusUpdate, CaseAssignRequest, CaseNoteCreate


class CaseService:
    """Case workflow, evidence attachment, and dispute manager."""

    @staticmethod
    async def create_case_for_transaction(
        db: AsyncSession,
        transaction_id: str,
        card_id: str,
        cardholder_id: str,
        amount: float,
        risk_score: float,
        decision_action: str,
        evidence: Optional[Dict[str, Any]] = None
    ) -> InvestigationCase:
        """Create a new triage case when an alert triggers."""
        # Check if a case already exists for this transaction
        stmt = select(InvestigationCase).where(InvestigationCase.transaction_id == transaction_id)
        res = await db.execute(stmt)
        existing = res.scalars().first()
        if existing:
            return existing

        # Assign severity based on risk score and action
        if risk_score >= 0.88 or decision_action == "DECLINE":
            severity = CaseSeverity.CRITICAL
            sla_hours = 2
        elif risk_score >= 0.65 or decision_action == "CHALLENGE_3DS":
            severity = CaseSeverity.HIGH
            sla_hours = 6
        else:
            severity = CaseSeverity.MEDIUM
            sla_hours = 24

        case_num = f"CASE-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:5].upper()}"

        new_case = InvestigationCase(
            case_number=case_num,
            transaction_id=transaction_id,
            card_id=card_id,
            cardholder_id=cardholder_id,
            amount=amount,
            risk_score=risk_score,
            severity=severity,
            status=CaseStatus.OPEN,
            summary=f"Automated risk alert triggered: action {decision_action} with score {risk_score:.3f}",
            evidence_payload=evidence or {},
            sla_due_at=datetime.now(timezone.utc) + timedelta(hours=sla_hours)
        )
        db.add(new_case)
        await db.commit()
        await db.refresh(new_case)
        return new_case

    @staticmethod
    async def list_cases(
        db: AsyncSession,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        assigned_to_me: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[InvestigationCase], int]:
        """Fetch filtered cases with pagination."""
        query = select(InvestigationCase).options(selectinload(InvestigationCase.notes))
        count_query = select(func.count(InvestigationCase.id))

        if status:
            query = query.where(InvestigationCase.status == status)
            count_query = count_query.where(InvestigationCase.status == status)
        if severity:
            query = query.where(InvestigationCase.severity == severity)
            count_query = count_query.where(InvestigationCase.severity == severity)
        if assigned_to_me:
            query = query.where(InvestigationCase.assigned_analyst_id == assigned_to_me)
            count_query = count_query.where(InvestigationCase.assigned_analyst_id == assigned_to_me)

        total = (await db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = query.order_by(InvestigationCase.created_at.desc()).offset(offset).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()
        return items, total

    @staticmethod
    async def get_case_by_id(db: AsyncSession, case_id: str) -> InvestigationCase:
        """Retrieve single case with notes."""
        stmt = (
            select(InvestigationCase)
            .options(selectinload(InvestigationCase.notes))
            .where((InvestigationCase.id == case_id) | (InvestigationCase.case_number == case_id))
        )
        result = await db.execute(stmt)
        case = result.scalars().first()
        if not case:
            raise EntityNotFoundException("InvestigationCase", case_id)
        return case

    @staticmethod
    async def update_status(
        db: AsyncSession,
        case_id: str,
        status_update: CaseStatusUpdate,
        user: User
    ) -> InvestigationCase:
        """Update case status and append resolution note."""
        case = await CaseService.get_case_by_id(db, case_id)
        case.status = CaseStatus(status_update.status)
        if status_update.resolution_reason:
            case.resolution_reason = status_update.resolution_reason

        # Automatically append audit note
        if status_update.note or status_update.resolution_reason:
            note_text = status_update.note or f"Status transitioned to {status_update.status}. Reason: {status_update.resolution_reason}"
            note = CaseNote(
                case_id=case.id,
                author_id=user.id,
                author_name=user.full_name,
                content=note_text
            )
            db.add(note)

        await db.commit()
        await db.refresh(case)
        return case

    @staticmethod
    async def assign_analyst(
        db: AsyncSession,
        case_id: str,
        assignment: CaseAssignRequest,
        actor: User
    ) -> InvestigationCase:
        """Assign analyst to open case."""
        case = await CaseService.get_case_by_id(db, case_id)
        case.assigned_analyst_id = assignment.analyst_id
        case.assigned_analyst_name = assignment.analyst_name
        if case.status == CaseStatus.OPEN:
            case.status = CaseStatus.IN_REVIEW

        note = CaseNote(
            case_id=case.id,
            author_id=actor.id,
            author_name=actor.full_name,
            content=f"Case assigned to {assignment.analyst_name}"
        )
        db.add(note)

        await db.commit()
        await db.refresh(case)
        return case

    @staticmethod
    async def add_note(
        db: AsyncSession,
        case_id: str,
        note_in: CaseNoteCreate,
        author: User
    ) -> CaseNote:
        """Add investigation note."""
        case = await CaseService.get_case_by_id(db, case_id)
        note = CaseNote(
            case_id=case.id,
            author_id=author.id,
            author_name=author.full_name,
            content=note_in.content,
            is_internal_only=note_in.is_internal_only or "true"
        )
        db.add(note)
        await db.commit()
        await db.refresh(note)
        return note
