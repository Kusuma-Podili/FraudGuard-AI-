"""SQLAlchemy Machine Learning Model Registry, Versioning, and A/B Testing Model."""

from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, Text
from backend.app.db.base import Base


class ModelRegistryRecord(Base):
    """ML model deployment catalog."""
    __tablename__ = "model_registries"

    model_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    version = Column(String(32), nullable=False)
    algorithm_type = Column(String(64), nullable=False)
    status = Column(String(32), default="CHAMPION")  # CHAMPION, CHALLENGER, CANDIDATE, RETIRED

    traffic_percentage = Column(Float, default=100.0)
    roc_auc = Column(Float, default=0.0)
    pr_auc = Column(Float, default=0.0)
    f1_score = Column(Float, default=0.0)
    p99_latency_ms = Column(Float, default=0.0)

    hyperparameters = Column(JSON, default=dict)
    feature_names = Column(JSON, default=list)
    description = Column(Text, nullable=True)
