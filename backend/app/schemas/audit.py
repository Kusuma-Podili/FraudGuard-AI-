"""Audit Trail and Compliance Log Schemas."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AuditLogResponse(BaseModel):
    id: str
    user_id: str
    user_email: str
    action_type: str
    resource_type: str
    resource_id: str
    change_summary: str
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
