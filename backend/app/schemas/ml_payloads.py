"""ML Model Metadata, Explainability, and Drift Schemas."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ModelRegistryResponse(BaseModel):
    id: str
    model_id: str
    name: str
    version: str
    algorithm_type: str
    status: str
    traffic_percentage: float
    roc_auc: float
    pr_auc: float
    f1_score: float
    p99_latency_ms: float
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExplainabilityRequest(BaseModel):
    transaction_id: Optional[str] = None
    transaction_payload: Optional[Dict[str, Any]] = None


class CounterfactualDTO(BaseModel):
    feature_name: str
    original_value: Any
    recommended_value: Any
    change_description: str
    is_actionable: bool


class ExplainabilityResponse(BaseModel):
    transaction_id: str
    risk_score: float
    base_value: float
    decision_action: str
    top_risk_factors: List[str]
    top_protective_factors: List[str]
    waterfall: List[Dict[str, Any]]
    counterfactuals: List[CounterfactualDTO] = []
    graph_syndicate_detected: bool = False
    graph_ring_telemetry: Dict[str, Any] = {}
