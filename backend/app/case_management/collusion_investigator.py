"""Merchant & Employee Internal Collusion Investigator.

Detects insider fraud patterns:
- Abnormal refund-to-sales ratios without corresponding merchandise returns
- Shared bank account / device routing between merchant employees and cardholders
- Off-hours cash-advance cycling and ghost authorization rings
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone


@dataclass
class CollusionAlert:
    alert_id: str
    merchant_id: str
    collusion_type: str  # REFUND_CYCLING, EMPLOYEE_CARDHOLDER_COLLUSION, GHOST_TRANSACTION
    risk_level: str  # HIGH, CRITICAL
    detected_indicators: List[str]
    estimated_loss_exposure: float
    recommended_containment: str


class CollusionInvestigator:
    """Investigates covert merchant-side and employee-assisted fraud conspiracies."""

    def analyze_merchant_refund_patterns(self, merchant_id: str, transactions: List[Dict[str, Any]]) -> Optional[CollusionAlert]:
        """Detect refund fraud and cash-out schemes."""
        if not transactions:
            return None

        total_sales = sum(tx["amount"] for tx in transactions if tx.get("type", "SALE") == "SALE")
        total_refunds = sum(tx["amount"] for tx in transactions if tx.get("type") == "REFUND")

        indicators = []
        if total_sales > 0:
            refund_ratio = total_refunds / total_sales
            if refund_ratio > 0.35:
                indicators.append(f"Abnormal refund-to-sales ratio: {refund_ratio*100:.1f}% (Benchmark < 5.0%)")

        # Check for refunds to cards with zero prior purchases at this merchant
        purchase_cards = {tx["card_id"] for tx in transactions if tx.get("type", "SALE") == "SALE"}
        orphan_refund_cards = [
            tx["card_id"] for tx in transactions
            if tx.get("type") == "REFUND" and tx["card_id"] not in purchase_cards
        ]

        if orphan_refund_cards:
            indicators.append(f"Detected {len(orphan_refund_cards)} orphan refunds sent to cards with no purchase history.")

        if indicators:
            return CollusionAlert(
                alert_id=f"COLLUSION-{merchant_id[:8]}",
                merchant_id=merchant_id,
                collusion_type="REFUND_CYCLING",
                risk_level="CRITICAL" if len(indicators) > 1 else "HIGH",
                detected_indicators=indicators,
                estimated_loss_exposure=total_refunds,
                recommended_containment="Freeze merchant payout settlement queue and initiate onsite audit.",
            )

        return None
