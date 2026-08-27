"""SQLAlchemy User, Role, and Authentication Session Models."""

import enum
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, DateTime
from backend.app.db.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    RISK_LEAD = "RISK_LEAD"
    FRAUD_ANALYST = "FRAUD_ANALYST"
    AUDITOR = "AUDITOR"


class User(Base):
    """User account entity."""
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.FRAUD_ANALYST, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    department = Column(String(100), default="Risk Operations")
    last_login_at = Column(DateTime, nullable=True)
