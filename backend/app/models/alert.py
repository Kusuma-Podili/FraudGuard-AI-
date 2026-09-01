"""Fraud Alert SQLAlchemy Model."""

import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Enum, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from backend.app.db.session import Base


class AlertSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, enum.Enum):
    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    CASE_CREATED = "CASE_CREATED"


class AlertRecord(Base):
    __tablename__ = "fraud_alerts"

    id = Column(String(36), primary_key=True, index=True)
    alert_id = Column(String(50), unique=True, index=True, nullable=False)
    transaction_id = Column(String(50), index=True, nullable=False)
    card_id = Column(String(50), index=True, nullable=False)
    cardholder_id = Column(String(50), index=True, nullable=True)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.MEDIUM, index=True)
    status = Column(Enum(AlertStatus), default=AlertStatus.NEW, index=True)
    risk_score = Column(Float, nullable=False)
    reason = Column(String(255), nullable=False)
    triggered_rules = Column(JSON, default=list)
    amount = Column(Float, default=0.0)
    merchant_name = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    assigned_to_user_id = Column(String(36), nullable=True)
    assigned_analyst_name = Column(String(100), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
