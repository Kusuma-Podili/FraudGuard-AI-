"""Alert Pydantic Schemas."""

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel


class AlertCreate(BaseModel):
    transaction_id: str
    card_id: str
    cardholder_id: Optional[str] = None
    severity: str = "MEDIUM"
    risk_score: float
    reason: str
    triggered_rules: List[str] = []
    amount: float = 0.0
    merchant_name: Optional[str] = None
    location: Optional[str] = None


class AlertStatusUpdate(BaseModel):
    status: str
    resolution_notes: Optional[str] = None


class AlertAssignRequest(BaseModel):
    analyst_id: str
    analyst_name: str


class AlertResponse(BaseModel):
    id: str
    alert_id: str
    transaction_id: str
    card_id: str
    cardholder_id: Optional[str] = None
    severity: str
    status: str
    risk_score: float
    reason: str
    triggered_rules: List[str] = []
    amount: float
    merchant_name: Optional[str] = None
    location: Optional[str] = None
    assigned_to_user_id: Optional[str] = None
    assigned_analyst_name: Optional[str] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
