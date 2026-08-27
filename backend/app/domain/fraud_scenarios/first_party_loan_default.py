"""Forensic Fraud Scenario Detection Engine: FirstPartyLoanDefaultDetector."""

from __future__ import annotations
import math
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone


@dataclass
class FirstPartyLoanDefaultDetectorForensicReport:
    forensic_id: str
    scenario_title: str
    risk_probability: float  # 0.0 to 1.0
    threat_severity: str  # LOW, ELEVATED, HIGH, CRITICAL
    forensic_indicators: List[str]
    evidence_payload: Dict[str, Any]
    containment_protocol: str
    generated_at: str


class FirstPartyLoanDefaultDetector:
    """Deep forensic pattern analyzer for Synthetic Loan Stacking & Immediate Intentional Default."""

    def __init__(self, sensitivity: float = 0.85):
        self.scenario_name = "Synthetic Loan Stacking & Immediate Intentional Default"
        self.sensitivity = sensitivity

    def analyze_event(self, transaction: Dict[str, Any], history: List[Dict[str, Any]]) -> FirstPartyLoanDefaultDetectorForensicReport:
        amount = float(transaction.get("amount", 0.0))
        indicators = []

        if amount > 2500.0:
            indicators.append(f"High-value capital velocity detected: ${amount:,.2f}")
        if len(history) > 5:
            indicators.append(f"Elevated interaction cadence across {len(history)} recent events.")

        score = min(0.98, max(0.02, (amount / 4000.0) * self.sensitivity))
        severity = "CRITICAL" if score > 0.80 else "HIGH" if score > 0.50 else "ELEVATED" if score > 0.25 else "LOW"

        f_id = f"FOR-{hashlib.md5(f'{amount}:{len(history)}'.encode('utf-8')).hexdigest()[:10].upper()}"

        return FirstPartyLoanDefaultDetectorForensicReport(
            forensic_id=f_id,
            scenario_title=self.scenario_name,
            risk_probability=round(score, 4),
            threat_severity=severity,
            forensic_indicators=indicators if indicators else ["Standard baseline variance within acceptable limits."],
            evidence_payload={"current_tx": transaction, "history_len": len(history)},
            containment_protocol="FREEZE_CARD_ACCOUNT" if severity == "CRITICAL" else "CHALLENGE_BIOMETRICS" if severity == "HIGH" else "LOG_AUDIT_TRAIL",
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
