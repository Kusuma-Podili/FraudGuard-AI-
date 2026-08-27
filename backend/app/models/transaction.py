"""SQLAlchemy Financial Transaction Record and Telemetry Model."""

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, Index
from backend.app.db.base import Base


class TransactionRecord(Base):
    """Financial transaction authorization record."""
    __tablename__ = "transactions"

    transaction_id = Column(String(64), unique=True, index=True, nullable=False)
    card_id = Column(String(64), index=True, nullable=False)
    cardholder_id = Column(String(64), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)

    # Merchant attributes
    merchant_id = Column(String(64), index=True, nullable=False)
    merchant_name = Column(String(255), nullable=True)
    merchant_category = Column(String(64), nullable=False)

    # Transaction metadata
    entry_mode = Column(String(32), default="E_COMMERCE")
    card_type = Column(String(32), default="CREDIT_STANDARD")
    card_network = Column(String(32), default="VISA")

    # Geolocation & Device
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    country_code = Column(String(2), default="US")
    device_fingerprint = Column(String(64), index=True, nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Evaluation Outcomes
    risk_score = Column(Float, nullable=False, default=0.0)
    decision_action = Column(String(32), default="ALLOW")  # ALLOW, REVIEW, CHALLENGE_3DS, DECLINE
    risk_tier = Column(String(32), default="LOW")          # LOW, MEDIUM, HIGH, CRITICAL

    # Triggers & Telemetry
    triggered_rules = Column(JSON, default=list)
    model_breakdown = Column(JSON, default=dict)
    is_fraud = Column(Integer, default=0)
    fraud_archetype = Column(String(64), default="LEGITIMATE")

    # Composite indices for high-frequency queries
    __table_args__ = (
        Index("ix_tx_card_created", "card_id", "created_at"),
        Index("ix_tx_score_action", "risk_score", "decision_action"),
    )
