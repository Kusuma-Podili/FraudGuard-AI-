"""Real-Time MLOps Alert Evaluator and Retraining Trigger Engine.

Evaluates operational health indicators (PSI drift, latency degradation,
false positive surges, precision drops) and dispatches automated alerts or retraining jobs.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


@dataclass
class MLOpsAlert:
    alert_id: str
    severity: str  # INFO, WARNING, CRITICAL
    alert_type: str # DRIFT_DETECTED, LATENCY_SPIKE, PRECISION_DROP, SCHEMA_VIOLATION
    description: str
    recommended_action: str
    timestamp: str


class AlertEvaluator:
    """Evaluates telemetry data against SLO thresholds."""

    def __init__(
        self,
        max_p99_latency_ms: float = 30.0,
        min_precision_threshold: float = 0.85,
        max_psi_threshold: float = 0.20
    ):
        self.max_p99_latency_ms = max_p99_latency_ms
        self.min_precision_threshold = min_precision_threshold
        self.max_psi_threshold = max_psi_threshold

    def evaluate_system_health(
        self,
        current_p99_latency_ms: float,
        current_precision: float,
        current_psi: float,
        error_rate: float = 0.0
    ) -> List[MLOpsAlert]:
        """Generate active alerts for anomalies violating operational thresholds."""
        alerts: List[MLOpsAlert] = []
        now_str = datetime.now(timezone.utc).isoformat()

        # 1. Latency check
        if current_p99_latency_ms > self.max_p99_latency_ms:
            alerts.append(MLOpsAlert(
                alert_id=f"ALT_LAT_{int(datetime.now(timezone.utc).timestamp())}",
                severity="CRITICAL" if current_p99_latency_ms > 2 * self.max_p99_latency_ms else "WARNING",
                alert_type="LATENCY_SPIKE",
                description=f"P99 latency ({current_p99_latency_ms:.1f}ms) breached SLO limit ({self.max_p99_latency_ms:.1f}ms)",
                recommended_action="Scale inference pods, check Redis cluster load, or enable tree pruning",
                timestamp=now_str
            ))

        # 2. Precision check
        if current_precision < self.min_precision_threshold:
            alerts.append(MLOpsAlert(
                alert_id=f"ALT_PREC_{int(datetime.now(timezone.utc).timestamp())}",
                severity="CRITICAL",
                alert_type="PRECISION_DROP",
                description=f"Model precision ({current_precision:.1%}) dropped below minimum acceptable floor ({self.min_precision_threshold:.1%})",
                recommended_action="Increase decline threshold or switch active traffic to Challenger model",
                timestamp=now_str
            ))

        # 3. Data Drift check
        if current_psi >= self.max_psi_threshold:
            alerts.append(MLOpsAlert(
                alert_id=f"ALT_DRIFT_{int(datetime.now(timezone.utc).timestamp())}",
                severity="CRITICAL" if current_psi > 0.25 else "WARNING",
                alert_type="DRIFT_DETECTED",
                description=f"Population Stability Index (PSI={current_psi:.3f}) indicates distribution shift in production features",
                recommended_action="Trigger automated retraining pipeline with fresh 14-day transaction partition",
                timestamp=now_str
            ))

        return alerts
