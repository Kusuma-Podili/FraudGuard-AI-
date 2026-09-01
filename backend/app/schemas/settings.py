"""System Settings & Risk Thresholds Pydantic Schemas."""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class RiskThresholdsConfig(BaseModel):
    low_max: float = 0.30  # 0.00 - 0.30 -> LOW (ALLOW)
    medium_max: float = 0.60  # 0.30 - 0.60 -> MEDIUM (MONITOR)
    high_max: float = 0.80  # 0.60 - 0.80 -> HIGH (REVIEW / CHALLENGE_3DS)
    critical_min: float = 0.80  # 0.80 - 1.00 -> CRITICAL (DECLINE)
    auto_decline_enabled: bool = True
    auto_case_creation_threshold: float = 0.60


class NotificationSettingsConfig(BaseModel):
    in_app_alerts_enabled: bool = True
    critical_alert_sound: bool = True
    email_digest_enabled: bool = False
    slack_webhook_url: Optional[str] = None
    min_alert_severity: str = "HIGH"


class SystemHealthStatus(BaseModel):
    backend_api: str = "HEALTHY"
    database: str = "HEALTHY"
    ml_engine: str = "HEALTHY"
    websocket: str = "HEALTHY"
    authentication: str = "HEALTHY"
    notification_service: str = "HEALTHY"
    p99_latency_ms: float = 14.2
    uptime_seconds: int = 86400
    active_connections: int = 12


class SystemSettingUpdate(BaseModel):
    setting_key: str
    setting_value: Dict[str, Any]
