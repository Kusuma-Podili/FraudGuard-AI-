"""SQLAlchemy Chargeback and Dispute Lifecycle Model."""

from sqlalchemy import Column, String, Float, DateTime, Text, JSON
from backend.app.db.base import Base


class ChargebackDispute(Base):
    """Cardholder payment dispute and chargeback representation."""
    __tablename__ = "chargeback_disputes"

    dispute_id = Column(String(64), unique=True, index=True, nullable=False)
    transaction_id = Column(String(64), index=True, nullable=False)
    card_id = Column(String(64), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")

    reason_code = Column(String(32), nullable=False)  # 10.4 (Fraud - Card-absent), 4837 (No cardholder auth)
    status = Column(String(32), default="REPRESENTMENT_FILED")  # PENDING, REPRESENTMENT_FILED, WON, LOST
    evidence_documents = Column(JSON, default=list)
    due_date = Column(DateTime, nullable=True)
    financial_outcome = Column(Float, nullable=True)
