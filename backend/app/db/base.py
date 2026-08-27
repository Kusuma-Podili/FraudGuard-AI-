"""SQLAlchemy Declarative Base with Timestamp Mixins and UUID ID Generators."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base, declared_attr


class CustomBase:
    """Custom base adding automated table naming and timestamps."""

    @declared_attr
    def __tablename__(cls) -> str:
        # Converts CamelCase model name to snake_case table name
        name = cls.__name__
        return "".join(["_" + c.lower() if c.isupper() else c for c in name]).lstrip("_") + "s"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


Base = declarative_base(cls=CustomBase)
