"""Investigation Case Management and Analyst Action Schemas."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CaseNoteCreate(BaseModel):
    content: str
    is_internal_only: Optional[str] = "true"


class CaseNoteResponse(BaseModel):
    id: str
    case_id: str
    author_name: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CaseStatusUpdate(BaseModel):
    status: str  # OPEN, IN_REVIEW, ESCALATED, CONFIRMED_FRAUD, FALSE_POSITIVE, RESOLVED
    resolution_reason: Optional[str] = None
    note: Optional[str] = None


class CaseAssignRequest(BaseModel):
    analyst_id: str
    analyst_name: str


class CaseResponse(BaseModel):
    id: str
    case_number: str
    transaction_id: str
    card_id: str
    cardholder_id: str
    amount: float
    risk_score: float
    severity: str
    status: str
    assigned_analyst_name: Optional[str] = None
    summary: Optional[str] = None
    resolution_reason: Optional[str] = None
    evidence_payload: Dict[str, Any] = {}
    created_at: datetime
    notes: List[CaseNoteResponse] = []

    model_config = ConfigDict(from_attributes=True)
