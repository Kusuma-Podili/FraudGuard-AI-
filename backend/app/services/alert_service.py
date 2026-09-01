"""Fraud Alert Management Service."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.alert import AlertRecord, AlertSeverity, AlertStatus
from backend.app.models.user import User
from backend.app.models.case import InvestigationCase, CaseSeverity, CaseStatus
from backend.app.models.audit_log import AuditLogRecord
from backend.app.schemas.alert import AlertCreate, AlertStatusUpdate, AlertAssignRequest
from backend.app.core.exceptions import EntityNotFoundException


class AlertService:

    @staticmethod
    async def create_alert(db: AsyncSession, alert_in: AlertCreate) -> AlertRecord:
        """Create a new fraud alert."""
        alert_id = f"ALT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        rec = AlertRecord(
            id=str(uuid.uuid4()),
            alert_id=alert_id,
            transaction_id=alert_in.transaction_id,
            card_id=alert_in.card_id,
            cardholder_id=alert_in.cardholder_id,
            severity=AlertSeverity(alert_in.severity),
            status=AlertStatus.NEW,
            risk_score=alert_in.risk_score,
            reason=alert_in.reason,
            triggered_rules=alert_in.triggered_rules,
            amount=alert_in.amount,
            merchant_name=alert_in.merchant_name,
            location=alert_in.location,
        )
        db.add(rec)
        await db.commit()
        await db.refresh(rec)
        return rec

    @staticmethod
    async def list_alerts(
        db: AsyncSession,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[AlertRecord], int]:
        """List alerts with filtering and pagination."""
        query = select(AlertRecord)
        count_query = select(func.count(AlertRecord.id))

        if status and status != "ALL":
            query = query.where(AlertRecord.status == status)
            count_query = count_query.where(AlertRecord.status == status)

        if severity and severity != "ALL":
            query = query.where(AlertRecord.severity == severity)
            count_query = count_query.where(AlertRecord.severity == severity)

        if search:
            search_pattern = f"%{search}%"
            filter_cond = (
                AlertRecord.alert_id.ilike(search_pattern) |
                AlertRecord.transaction_id.ilike(search_pattern) |
                AlertRecord.card_id.ilike(search_pattern) |
                AlertRecord.merchant_name.ilike(search_pattern) |
                AlertRecord.reason.ilike(search_pattern)
            )
            query = query.where(filter_cond)
            count_query = count_query.where(filter_cond)

        total = (await db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = query.order_by(desc(AlertRecord.created_at)).offset(offset).limit(page_size)

        res = await db.execute(query)
        return res.scalars().all(), total

    @staticmethod
    async def get_alert_by_id(db: AsyncSession, alert_id: str) -> AlertRecord:
        """Retrieve single alert by ID or alert_id."""
        stmt = select(AlertRecord).where((AlertRecord.id == alert_id) | (AlertRecord.alert_id == alert_id))
        res = await db.execute(stmt)
        alert = res.scalars().first()
        if not alert:
            raise EntityNotFoundException(f"Alert {alert_id} not found")
        return alert

    @staticmethod
    async def update_alert_status(
        db: AsyncSession,
        alert_id: str,
        update_in: AlertStatusUpdate,
        actor: User
    ) -> AlertRecord:
        """Update alert status and log audit trail."""
        alert = await AlertService.get_alert_by_id(db, alert_id)
        prev_status = alert.status.value if hasattr(alert.status, 'value') else str(alert.status)
        alert.status = AlertStatus(update_in.status)
        if update_in.resolution_notes:
            alert.resolution_notes = update_in.resolution_notes

        audit_log = AuditLogRecord(
            id=str(uuid.uuid4()),
            user_id=actor.id,
            user_email=actor.email,
            action_type="ALERT_STATUS_UPDATE",
            resource_type="ALERT",
            resource_id=alert.alert_id,
            change_summary=f"Alert status updated from {prev_status} to {update_in.status}",
            ip_address="127.0.0.1",
            before_state={"status": prev_status},
            after_state={"status": update_in.status, "notes": update_in.resolution_notes}
        )
        db.add(audit_log)
        await db.commit()
        await db.refresh(alert)
        return alert

    @staticmethod
    async def assign_alert(
        db: AsyncSession,
        alert_id: str,
        assign_in: AlertAssignRequest,
        actor: User
    ) -> AlertRecord:
        """Assign alert to an analyst."""
        alert = await AlertService.get_alert_by_id(db, alert_id)
        alert.assigned_to_user_id = assign_in.analyst_id
        alert.assigned_analyst_name = assign_in.analyst_name
        alert.status = AlertStatus.ASSIGNED

        audit_log = AuditLogRecord(
            id=str(uuid.uuid4()),
            user_id=actor.id,
            user_email=actor.email,
            action_type="ALERT_ASSIGNMENT",
            resource_type="ALERT",
            resource_id=alert.alert_id,
            change_summary=f"Alert assigned to {assign_in.analyst_name}",
            ip_address="127.0.0.1",
            after_state={"assigned_analyst": assign_in.analyst_name, "assigned_id": assign_in.analyst_id}
        )
        db.add(audit_log)
        await db.commit()
        await db.refresh(alert)
        return alert

    @staticmethod
    async def convert_to_case(
        db: AsyncSession,
        alert_id: str,
        actor: User
    ) -> Tuple[AlertRecord, InvestigationCase]:
        """Convert a high-priority alert into a formal fraud case."""
        alert = await AlertService.get_alert_by_id(db, alert_id)
        alert.status = AlertStatus.CASE_CREATED

        case_num = f"CASE-{datetime.now().strftime('%Y')}-{uuid.uuid4().hex[:5].upper()}"
        sev_map = {
            AlertSeverity.CRITICAL: CaseSeverity.CRITICAL,
            AlertSeverity.HIGH: CaseSeverity.HIGH,
            AlertSeverity.MEDIUM: CaseSeverity.MEDIUM,
            AlertSeverity.LOW: CaseSeverity.LOW,
        }
        case = InvestigationCase(
            case_number=case_num,
            transaction_id=alert.transaction_id,
            card_id=alert.card_id,
            cardholder_id=alert.cardholder_id or f"USR_{alert.card_id[-5:]}",
            amount=alert.amount,
            risk_score=alert.risk_score,
            severity=sev_map.get(alert.severity, CaseSeverity.HIGH),
            status=CaseStatus.OPEN,
            summary=f"Escalated from Alert {alert.alert_id}: {alert.reason}",
            assigned_analyst_id=actor.id,
            assigned_analyst_name=actor.full_name,
            evidence_payload={"alert_id": alert.alert_id, "triggered_rules": alert.triggered_rules, "reason": alert.reason}
        )
        db.add(case)

        audit_log = AuditLogRecord(
            id=str(uuid.uuid4()),
            user_id=actor.id,
            user_email=actor.email,
            action_type="ALERT_CONVERTED_TO_CASE",
            resource_type="CASE",
            resource_id=alert.alert_id,
            change_summary=f"Alert escalated into investigation case {case_num}",
            ip_address="127.0.0.1",
            after_state={"case_number": case_num}
        )
        db.add(audit_log)
        await db.commit()
        await db.refresh(alert)
        await db.refresh(case)
        return alert, case
