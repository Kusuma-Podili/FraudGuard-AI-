"""Analytics, Dashboard KPIs, and Stream Telemetry Schemas."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class DashboardSummaryKPIs(BaseModel):
    total_transactions_24h: int
    total_volume_usd_24h: float
    fraud_prevented_usd_24h: float
    fraud_rate_percentage: float
    active_threat_level: str  # NORMAL, ELEVATED, HIGH, SEVERE
    open_cases_count: int
    avg_inference_latency_ms: float
    p99_inference_latency_ms: float
    system_tps: float


class HourlyFraudTrend(BaseModel):
    hour: str
    total_count: int
    fraud_count: int
    volume_usd: float
    blocked_volume_usd: float


class MerchantRiskProfileDTO(BaseModel):
    merchant_id: str
    name: str
    category: str
    risk_score: float
    fraud_rate: float
    total_volume: float
    is_blacklisted: bool


class GeoRiskMetricDTO(BaseModel):
    country_code: str
    country_name: str
    risk_score: float
    transaction_count: int
    fraud_count: int


class SimulationControlRequest(BaseModel):
    action: str  # START, STOP, PAUSE, RESUME, SET_SPEED, INJECT_ATTACK
    target_tps: Optional[int] = 5
    attack_type: Optional[str] = None  # CARD_TESTING, IMPOSSIBLE_TRAVEL, ATO, CRYPTO_SURGE
    duration_seconds: Optional[int] = 30
