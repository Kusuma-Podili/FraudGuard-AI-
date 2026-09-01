"""System Configuration & Risk Thresholds SQLAlchemy Model."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, JSON
from backend.app.db.session import Base


class SystemSettingRecord(Base):
    __tablename__ = "system_settings"

    id = Column(String(36), primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, index=True, nullable=False)
    setting_value = Column(JSON, nullable=False)
    category = Column(String(50), default="GENERAL")  # RISK_THRESHOLDS, NOTIFICATIONS, SYSTEM
    description = Column(Text, nullable=True)
    updated_by_user_id = Column(String(36), nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
