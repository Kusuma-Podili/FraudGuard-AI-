"""Customer Profile & Card Pydantic Schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class CustomerProfileResponse(BaseModel):
    id: str
    customer_id: str
    card_id: str
    masked_card: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    card_type: str = "CREDIT"
    card_network: str = "VISA"
    card_status: str = "ACTIVE"
    risk_tier: str = "LOW"
    avg_amount_30d: float = 120.0
    max_amount_single: float = 1500.0
    typical_categories: List[str] = []
    typical_locations: List[str] = []
    known_devices: List[str] = []
    total_transactions_count: int = 0
    total_fraud_alerts_count: int = 0
    total_cases_count: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerProfileUpdate(BaseModel):
    card_status: Optional[str] = None
    risk_tier: Optional[str] = None
    is_active: Optional[bool] = None
