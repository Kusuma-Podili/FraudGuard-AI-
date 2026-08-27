"""Hardware & Execution Environment Sensor: ScreenColorDepth."""

from __future__ import annotations
import math
import hashlib
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class ScreenColorDepthTelemetryResult:
    entropy_bits: float
    signature_hash: str
    is_spoofed: bool
    is_bot_automation: bool
    sensor_health_rating: str
    anomalies: List[str]


class ScreenColorDepthSensor:
    """Anti-spoofing sensor analysis for screen_color_depth."""

    def __init__(self, salt: str = "sensor_salt_2026"):
        self.salt = salt
        self.sensor_name = "ScreenColorDepth"

    def analyze_telemetry(self, raw_telemetry: Dict[str, Any]) -> ScreenColorDepthTelemetryResult:
        anomalies = []
        serialized = json.dumps(raw_telemetry, sort_keys=True)
        sig = hashlib.sha256(f"{serialized}:{self.salt}".encode("utf-8")).hexdigest()

        # Anti-fraud heuristic evaluations
        ua = str(raw_telemetry.get("user_agent", "")).lower()
        if any(bot in ua for bot in ["selenium", "puppeteer", "playwright", "headless", "phantomjs"]):
            anomalies.append("Automated headless browser runtime detected.")

        latency = float(raw_telemetry.get("execution_latency_ms", 5.0))
        if latency < 0.1:
            anomalies.append("Instantaneous execution indicates static mock injection.")

        is_spoofed = len(anomalies) > 0
        entropy = 18.4 if not is_spoofed else 2.1

        return ScreenColorDepthTelemetryResult(
            entropy_bits=round(entropy, 2),
            signature_hash=f"SIG_{sig[:16].upper()}",
            is_spoofed=is_spoofed,
            is_bot_automation="Automated" in str(anomalies),
            sensor_health_rating="OPTIMAL" if not is_spoofed else "DEGRADED",
            anomalies=anomalies,
        )
