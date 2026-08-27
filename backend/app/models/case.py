"""SQLAlchemy Fraud Case Management and Investigation Workflow Model."""

import enum
from sqlalchemy import Column, String, Float, Enum as SQLEnum, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class CaseStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_REVIEW = "IN_REVIEW"
    ESCALATED = "ESCALATED"
    CONFIRMED_FRAUD = "CONFIRMED_FRAUD"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    CHARGEBACK_FILED = "CHARGEBACK_FILED"
    RESOLVED = "RESOLVED"


class CaseSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class InvestigationCase(Base):
    """Investigation case container for suspicious transaction triage."""
    __tablename__ = "investigation_cases"

    case_number = Column(String(32), unique=True, index=True, nullable=False)
    transaction_id = Column(String(64), index=True, nullable=False)
    card_id = Column(String(64), index=True, nullable=False)
    cardholder_id = Column(String(64), index=True, nullable=False)

    amount = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    severity = Column(SQLEnum(CaseSeverity), default=CaseSeverity.MEDIUM, nullable=False)
    status = Column(SQLEnum(CaseStatus), default=CaseStatus.OPEN, index=True, nullable=False)

    assigned_analyst_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    assigned_analyst_name = Column(String(255), nullable=True)

    summary = Column(String(500), nullable=True)
    resolution_reason = Column(String(255), nullable=True)
    evidence_payload = Column(JSON, default=dict)
    sla_due_at = Column(DateTime, nullable=True)

    # Relationships
    notes = relationship("CaseNote", back_populates="case", cascade="all, delete-orphan")


class CaseNote(Base):
    """Analyst note entry attached to an investigation case."""
    __tablename__ = "case_notes"

    case_id = Column(String(36), ForeignKey("investigation_cases.id"), nullable=False)
    author_id = Column(String(36), nullable=False)
    author_name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_internal_only = Column(String(10), default="true")

    case = relationship("InvestigationCase", back_populates="notes")
