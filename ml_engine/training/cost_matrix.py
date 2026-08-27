"""Financial Cost Matrix and Revenue Optimization Model for Fraud Decisions.

In corporate fraud management, maximizing statistical accuracy or F1-score is secondary
to maximizing dollar savings while minimizing customer insult rates (false decline friction).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import numpy as np


@dataclass
class CostEvaluationSummary:
    total_transactions: int
    fraud_transactions: int
    fraud_dollars_at_risk: float
    fraud_dollars_prevented: float
    fraud_dollars_lost_chargebacks: float
    chargeback_penalties_paid: float
    false_decline_customer_friction_cost: float
    manual_review_labor_cost: float
    net_economic_savings_usd: float
    roi_percentage: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_transactions": self.total_transactions,
            "fraud_transactions": self.fraud_transactions,
            "fraud_dollars_at_risk": round(self.fraud_dollars_at_risk, 2),
            "fraud_dollars_prevented": round(self.fraud_dollars_prevented, 2),
            "fraud_dollars_lost_chargebacks": round(self.fraud_dollars_lost_chargebacks, 2),
            "chargeback_penalties_paid": round(self.chargeback_penalties_paid, 2),
            "false_decline_customer_friction_cost": round(self.false_decline_customer_friction_cost, 2),
            "manual_review_labor_cost": round(self.manual_review_labor_cost, 2),
            "net_economic_savings_usd": round(self.net_economic_savings_usd, 2),
            "roi_percentage": round(self.roi_percentage, 2),
        }


class FinancialCostMatrix:
    """Calculates financial P&L outcomes of decision boundaries."""

    def __init__(
        self,
        chargeback_fee_usd: float = 35.00,
        manual_review_cost_usd: float = 12.00,
        false_decline_churn_multiplier: float = 0.08  # 8% of transaction value lost in lifetime customer value
    ):
        self.chargeback_fee_usd = chargeback_fee_usd
        self.manual_review_cost_usd = manual_review_cost_usd
        self.false_decline_churn_multiplier = false_decline_churn_multiplier

    def evaluate_financial_pnl(
        self,
        amounts: np.ndarray,
        y_true: np.ndarray,
        decisions: List[str]
    ) -> CostEvaluationSummary:
        """Compute dollar outcomes for batch decisions."""
        n_samples = len(y_true)
        fraud_mask = (y_true == 1)

        total_risk_dollars = float(np.sum(amounts[fraud_mask]))

        prevented_dollars = 0.0
        lost_dollars = 0.0
        chargeback_fees = 0.0
        friction_cost = 0.0
        review_labor_cost = 0.0

        for i in range(n_samples):
            amt = float(amounts[i])
            actual_fraud = bool(fraud_mask[i])
            action = decisions[i]

            if action == "DECLINE":
                if actual_fraud:
                    prevented_dollars += amt
                else:
                    friction_cost += (amt * self.false_decline_churn_multiplier)
            elif action == "CHALLENGE_3DS":
                if actual_fraud:
                    prevented_dollars += amt * 0.95  # 95% of fraud abandoned at 3DS step
                    lost_dollars += amt * 0.05
                else:
                    friction_cost += 2.00  # Minor friction fee
            elif action == "REVIEW":
                review_labor_cost += self.manual_review_cost_usd
                if actual_fraud:
                    prevented_dollars += amt * 0.90  # 90% caught by human analyst
                    lost_dollars += amt * 0.10
            elif action == "ALLOW":
                if actual_fraud:
                    lost_dollars += amt
                    chargeback_fees += self.chargeback_fee_usd

        net_savings = prevented_dollars - (lost_dollars + chargeback_fees + friction_cost + review_labor_cost)
        total_costs = lost_dollars + chargeback_fees + friction_cost + review_labor_cost
        roi = (net_savings / max(total_costs, 1.0)) * 100.0

        return CostEvaluationSummary(
            total_transactions=n_samples,
            fraud_transactions=int(np.sum(fraud_mask)),
            fraud_dollars_at_risk=total_risk_dollars,
            fraud_dollars_prevented=prevented_dollars,
            fraud_dollars_lost_chargebacks=lost_dollars,
            chargeback_penalties_paid=chargeback_fees,
            false_decline_customer_friction_cost=friction_cost,
            manual_review_labor_cost=review_labor_cost,
            net_economic_savings_usd=net_savings,
            roi_percentage=roi
        )
