"""Transaction Ingestion, Evaluation, and Telemetry Schemas."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class TransactionEvaluationRequest(BaseModel):
    """Raw transaction payload submitted to inference gateway."""
    transaction_id: Optional[str] = None
    card_id: str
    cardholder_id: Optional[str] = None
    amount: float = Field(..., gt=0.0, description="Authorization amount")
    currency: str = "USD"

    merchant_id: str
    merchant_name: Optional[str] = None
    merchant_category: str = "GENERAL_RETAIL"

    entry_mode: str = "E_COMMERCE"
    card_type: str = "CREDIT_STANDARD"
    card_network: str = "VISA"

    latitude: Optional[float] = 37.7749
    longitude: Optional[float] = -122.4194
    country_code: str = "US"

    device_type: str = "MOBILE_APP"
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None
    failed_pin_attempts_24h: int = 0
    timestamp: Optional[str] = None


class DecisionResponse(BaseModel):
    """Decision output returned to payment switch (<20ms)."""
    transaction_id: str
    decision_action: str  # ALLOW, REVIEW, CHALLENGE_3DS, DECLINE
    risk_score: float     # 0.000 to 1.000
    risk_tier: str        # LOW, MEDIUM, HIGH, CRITICAL
    confidence_level: str # LOW, MEDIUM, HIGH, VERY_HIGH

    triggered_rules: List[Dict[str, Any]] = []
    model_breakdown: Dict[str, float] = {}
    is_anomaly: bool = False
    is_impossible_travel: bool = False
    requires_step_up_auth: bool = False

    latency_ms: float
    evaluated_at: str

    model_config = ConfigDict(from_attributes=True)


class TransactionResponse(BaseModel):
    """Full stored transaction record with telemetry."""
    id: str
    transaction_id: str
    card_id: str
    cardholder_id: str
    amount: float
    currency: str
    merchant_id: str
    merchant_name: Optional[str] = None
    merchant_category: str
    entry_mode: str
    card_type: str
    card_network: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    country_code: str
    device_fingerprint: Optional[str] = None
    ip_address: Optional[str] = None
    risk_score: float
    decision_action: str
    risk_tier: str
    triggered_rules: List[Any] = []
    model_breakdown: Dict[str, Any] = {}
    fraud_archetype: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
