"""Customer Profile & Card Behavioral Baseline SQLAlchemy Model."""

import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, Text
from backend.app.db.session import Base


class CustomerRiskTier(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    id = Column(String(36), primary_key=True, index=True)
    customer_id = Column(String(50), unique=True, index=True, nullable=False)
    card_id = Column(String(50), unique=True, index=True, nullable=False)
    masked_card = Column(String(30), nullable=False)  # e.g. **** **** **** 4829
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(50), nullable=True)
    card_type = Column(String(30), default="CREDIT")
    card_network = Column(String(30), default="VISA")
    card_status = Column(String(30), default="ACTIVE")  # ACTIVE, FROZEN, BLOCKED
    risk_tier = Column(String(20), default="LOW")
    avg_amount_30d = Column(Float, default=120.0)
    max_amount_single = Column(Float, default=1500.0)
    typical_categories = Column(JSON, default=list)  # ["GROCERY", "RESTAURANT", "GAS"]
    typical_locations = Column(JSON, default=list)  # ["New York, US", "Jersey City, US"]
    known_devices = Column(JSON, default=list)  # ["dev_fp_apple_safari_1", "dev_fp_iphone_app"]
    total_transactions_count = Column(Integer, default=45)
    total_fraud_alerts_count = Column(Integer, default=0)
    total_cases_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
