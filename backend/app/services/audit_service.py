"""Compliance Audit Trail Service."""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.audit_log import AuditLogRecord
from backend.app.models.user import User


class AuditService:
    """Records immutable compliance logs for regulatory auditing."""

    @staticmethod
    async def log_action(
        db: AsyncSession,
        user: User,
        action_type: str,
        resource_type: str,
        resource_id: str,
        summary: str,
        before_state: Optional[Dict[str, Any]] = None,
        after_state: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> AuditLogRecord:
        """Create audit log entry."""
        log = AuditLogRecord(
            user_id=user.id,
            user_email=user.email,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            change_summary=summary,
            before_state=before_state,
            after_state=after_state,
            ip_address=ip_address
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log
