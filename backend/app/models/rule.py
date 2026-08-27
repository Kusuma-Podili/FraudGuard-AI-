"""SQLAlchemy Dynamic Business Rules and Rule Execution Audit Model."""

import enum
from sqlalchemy import Column, String, Integer, Float, Boolean, Enum as SQLEnum, Text, JSON
from backend.app.db.base import Base


class RuleAction(str, enum.Enum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    CHALLENGE_3DS = "CHALLENGE_3DS"
    DECLINE = "DECLINE"
    TAG_SUSPICIOUS = "TAG_SUSPICIOUS"


class FraudRule(Base):
    """Declarative fraud rule evaluated by the AST engine."""
    __tablename__ = "fraud_rules"

    rule_code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(64), default="VELOCITY")  # VELOCITY, AMOUNT, GEO, MERCHANT, CREDENTIALS

    condition_expression = Column(Text, nullable=False)  # AST expression e.g. "amount > 5000 AND velocity_1h > 3"
    action = Column(SQLEnum(RuleAction), default=RuleAction.REVIEW, nullable=False)
    priority = Column(Integer, default=100)  # Lower number = higher priority
    is_active = Column(Boolean, default=True, index=True, nullable=False)

    total_triggered_count = Column(Integer, default=0)
    fraud_precision_rate = Column(Float, default=0.0)
    created_by_user_id = Column(String(36), nullable=True)
