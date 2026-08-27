"""Business Rule Configuration and AST Backtesting Schemas."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class RuleCreate(BaseModel):
    rule_code: str
    name: str
    description: Optional[str] = None
    category: str = "VELOCITY"
    condition_expression: str
    action: str = "REVIEW"
    priority: int = 100
    is_active: bool = True


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    condition_expression: Optional[str] = None
    action: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class RuleDryRunRequest(BaseModel):
    condition_expression: str
    sample_transaction: Dict[str, Any]


class RuleDryRunResponse(BaseModel):
    is_triggered: bool
    evaluation_result: bool
    latency_microseconds: float
    matched_variables: Dict[str, Any]
    error_message: Optional[str] = None


class RuleBacktestRequest(BaseModel):
    condition_expression: str
    historical_samples_count: int = 500


class RuleBacktestResponse(BaseModel):
    total_evaluated: int
    total_triggered: int
    trigger_percentage: float
    fraud_catch_rate: float
    false_positive_rate: float
    estimated_monthly_decline_volume: int


class RuleResponse(BaseModel):
    id: str
    rule_code: str
    name: str
    description: Optional[str] = None
    category: str
    condition_expression: str
    action: str
    priority: int
    is_active: bool
    total_triggered_count: int
    fraud_precision_rate: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
