"""SQLAlchemy Merchant Entity and Risk Profile Model."""

from sqlalchemy import Column, String, Float, Integer, Boolean, JSON
from backend.app.db.base import Base


class MerchantEntity(Base):
    """Merchant entity risk profile."""
    __tablename__ = "merchants"

    merchant_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(64), nullable=False, index=True)
    country_code = Column(String(2), default="US")
    risk_score = Column(Float, default=0.05)
    is_blacklisted = Column(Boolean, default=False, index=True)

    total_volume_30d = Column(Float, default=0.0)
    total_transactions_30d = Column(Integer, default=0)
    fraud_rate_30d = Column(Float, default=0.0)
    chargeback_rate_30d = Column(Float, default=0.0)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
