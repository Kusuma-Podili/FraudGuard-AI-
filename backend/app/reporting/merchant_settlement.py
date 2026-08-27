"""Merchant Risk Tiering & Rolling Reserve Settlement Engine.

Computes dynamically adjusted rolling reserve escrow balances (5% - 25% withheld for 180 days)
for high-risk merchant categories (crypto exchanges, gambling, adult, travel) based on chargeback ratios.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta, timezone


@dataclass
class SettlementStatement:
    merchant_id: str
    settlement_cycle_date: str
    gross_sales: float
    total_interchange_fees: float
    total_refunds: float
    total_chargebacks: float
    withheld_rolling_reserve_amount: float
    net_payout_amount: float
    applied_reserve_percentage: float
    merchant_risk_tier: str  # TIER_1_LOW, TIER_2_STANDARD, TIER_3_ELEVATED, TIER_4_HIGH_RISK


class MerchantSettlementEngine:
    """Calculates risk-adjusted merchant payouts, fee deductions, and rolling reserves."""

    def evaluate_merchant_tier(self, chargeback_ratio: float, category: str) -> Tuple[str, float]:
        """Determine merchant risk classification and mandatory rolling reserve percentage."""
        if category in ("CRYPTO_EXCHANGE", "GAMBLING") or chargeback_ratio > 0.015:
            return "TIER_4_HIGH_RISK", 0.20  # 20% reserve
        elif category in ("LUXURY_JEWELRY", "TRAVEL_AIRLINE") or chargeback_ratio > 0.008:
            return "TIER_3_ELEVATED", 0.10  # 10% reserve
        elif chargeback_ratio > 0.004:
            return "TIER_2_STANDARD", 0.05   # 5% reserve
        else:
            return "TIER_1_LOW", 0.00        # 0% reserve

    def generate_settlement_batch(
        self,
        merchant_id: str,
        category: str,
        sales_amount: float,
        refunds_amount: float,
        chargeback_amount: float,
        interchange_cost: float,
    ) -> SettlementStatement:
        """Compute full settlement batch statement."""
        cb_ratio = (chargeback_amount / sales_amount) if sales_amount > 0 else 0.0
        tier, reserve_pct = self.evaluate_merchant_tier(cb_ratio, category)

        withheld_reserve = round(sales_amount * reserve_pct, 2)
        net_payout = round(sales_amount - refunds_amount - chargeback_amount - interchange_cost - withheld_reserve, 2)

        return SettlementStatement(
            merchant_id=merchant_id,
            settlement_cycle_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            gross_sales=round(sales_amount, 2),
            total_interchange_fees=round(interchange_cost, 2),
            total_refunds=round(refunds_amount, 2),
            total_chargebacks=round(chargeback_amount, 2),
            withheld_rolling_reserve_amount=withheld_reserve,
            net_payout_amount=max(0.0, net_payout),
            applied_reserve_percentage=reserve_pct,
            merchant_risk_tier=tier,
        )
