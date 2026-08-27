"""SQLAlchemy Immutable Compliance Audit Log Model."""

from sqlalchemy import Column, String, JSON, Text
from backend.app.db.base import Base


class AuditLogRecord(Base):
    """Immutable audit trail of analyst and administrative activities."""
    __tablename__ = "audit_logs"

    user_id = Column(String(36), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)
    action_type = Column(String(64), nullable=False, index=True)  # CASE_RESOLVED, RULE_CREATED, MODEL_PROMOTED
    resource_type = Column(String(64), nullable=False)           # CASE, RULE, MODEL, CONFIG
    resource_id = Column(String(64), nullable=False)

    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    change_summary = Column(Text, nullable=False)
    before_state = Column(JSON, nullable=True)
    after_state = Column(JSON, nullable=True)
