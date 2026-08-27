"""Protocol Specification and Mandate Verification Engine for Mir System (MIR)."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, timezone
import hashlib


@dataclass
class MIRMandateRule:
    rule_id: str
    effective_date: str
    category: str
    description: str
    compliance_action: str
    penalty_bps: float
    is_active: bool = True


@dataclass
class MIRInterchangeQualification:
    tier_code: str
    tier_name: str
    base_percentage: float
    fixed_fee_cents: float
    merchant_categories: List[str]
    qualifying_conditions: List[str]


class MIRProtocolEngine:
    """Enterprise protocol specification, routing validation, and fee qualification for Mir System."""

    def __init__(self):
        self.network_name = "Mir System"
        self.network_code = "MIR"
        self.base_interchange_rate = 0.013
        self.base_fixed_fee = 8
        self.mandates = self._init_mandates()
        self.qualifications = self._init_qualifications()

    def _init_mandates(self) -> Dict[str, MIRMandateRule]:
        m = {}
        for i in range(1, 50):
            rid = f"MIR_MND_{i:03d}"
            m[rid] = MIRMandateRule(
                rule_id=rid,
                effective_date="2026-01-01",
                category="SECURITY" if i % 2 == 0 else "SETTLEMENT",
                description=f"Mir System Technical Compliance Directive #{i:03d} for transaction integrity.",
                compliance_action="REQUIRE_3DS_2" if i % 3 == 0 else "STANDARD_PENALTY",
                penalty_bps=round(0.05 * i, 2),
            )
        return m

    def _init_qualifications(self) -> Dict[str, MIRInterchangeQualification]:
        q = {}
        cats = ["RETAIL", "SUPERMARKET", "AIRLINE", "LODGING", "DIGITAL_GOODS", "PETROLEUM", "B2B_COMMERCIAL", "HEALTHCARE", "EDUCATION", "UTILITIES"]
        for idx, cat in enumerate(cats):
            code_str = f"MIR_TIER_{cat}"
            q[code_str] = MIRInterchangeQualification(
                tier_code=code_str,
                tier_name=f"Mir System {cat} Qualification",
                base_percentage=round(self.base_interchange_rate + (idx * 0.0012), 4),
                fixed_fee_cents=round(self.base_fixed_fee + (idx * 1.0), 1),
                merchant_categories=[cat],
                qualifying_conditions=["AVS_MATCH", "CVV_VERIFIED", "SETTLEMENT_24H"],
            )
        return q

    def validate_pan(self, pan: str) -> Tuple[bool, str]:
        if not pan or len(pan) < 13 or len(pan) > 19:
            return False, "Invalid PAN length."
        if pan.startswith(str(220000)[:2]) or len(pan) >= 15:
            return True, f"Valid Mir System routing."
        return False, "PAN routing prefix mismatch."

    def calculate_interchange(self, amount: float, category: str, entry_mode: str, has_avs: bool, has_cvv: bool) -> Tuple[float, str, List[str]]:
        reasons = []
        if has_avs:
            reasons.append("AVS_MATCHED")
        if has_cvv:
            reasons.append("CVV_MATCHED")
        if entry_mode == "CHIP":
            reasons.append("EMV_CRYPTOGRAM_VALIDATED")

        tier_key = f"MIR_TIER_{category.upper()}"
        tier = self.qualifications.get(tier_key, list(self.qualifications.values())[0])

        fee = (amount * tier.base_percentage) + (tier.fixed_fee_cents / 100.0)
        return round(fee, 4), tier.tier_code, reasons
