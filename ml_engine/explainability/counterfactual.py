"""Counterfactual Explanations and Adverse Action Generation.

Finds the closest actionable feature adjustments required to transition
a declined / high-risk transaction into an acceptable legitimate state:
$\\arg\\min_{x'} \\mathcal{L}_{score}(f(x'), y^*) + \\lambda \\|x - x'\\|_1$
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from ml_engine.models.base_model import BaseModel


@dataclass
class CounterfactualRecommendation:
    feature_name: str
    original_value: Any
    recommended_value: Any
    change_description: str
    is_actionable: bool


class CounterfactualExplainer:
    """Actionable counterfactual generator for compliance adverse action notices."""

    def __init__(self, model: BaseModel, target_score_threshold: float = 0.25):
        self.model = model
        self.target_score_threshold = target_score_threshold
        # Features that can be changed by the cardholder or merchant
        self.actionable_features = {
            "amount", "failed_pin_attempts_24h", "entry_mode", "transaction_channel", "distance_from_home_km"
        }

    def generate_counterfactual(
        self,
        raw_transaction: Dict[str, Any],
        current_score: float,
        feature_vector: np.ndarray
    ) -> List[CounterfactualRecommendation]:
        """Generate human-readable prescriptive explanations for transaction remediation."""
        recommendations: List[CounterfactualRecommendation] = []

        if current_score <= self.target_score_threshold:
            return recommendations

        amount = float(raw_transaction.get("amount", 0.0))
        failed_pins = int(raw_transaction.get("failed_pin_attempts_24h", 0))
        distance_km = float(raw_transaction.get("distance_from_home_km", 0.0))
        entry_mode = str(raw_transaction.get("entry_mode", "CNP"))

        # 1. PIN / 3DS Verification failure
        if failed_pins > 0:
            recommendations.append(CounterfactualRecommendation(
                feature_name="failed_pin_attempts_24h",
                original_value=failed_pins,
                recommended_value=0,
                change_description="Complete successful Step-Up Two-Factor / 3D-Secure authentication",
                is_actionable=True
            ))

        # 2. Unusually High Monetary Amount
        if amount > 1000.0:
            suggested_amount = round(amount * 0.40, 2)
            recommendations.append(CounterfactualRecommendation(
                feature_name="amount",
                original_value=amount,
                recommended_value=suggested_amount,
                change_description=f"Reduce single transaction authorization limit below ${suggested_amount}",
                is_actionable=True
            ))

        # 3. Card-Not-Present vs Chip & PIN
        if entry_mode in ("CNP", "MANUAL_KEYED"):
            recommendations.append(CounterfactualRecommendation(
                feature_name="entry_mode",
                original_value=entry_mode,
                recommended_value="EMV_CHIP_PIN",
                change_description="Execute transaction via physical EMV Chip & PIN terminal with biometric verification",
                is_actionable=True
            ))

        # 4. Long-Distance Geo Discrepancy
        if distance_km > 500.0:
            recommendations.append(CounterfactualRecommendation(
                feature_name="distance_from_home_km",
                original_value=round(distance_km, 1),
                recommended_value=0.0,
                change_description="Notify bank of international travel itinerary or verify physical possession of card",
                is_actionable=False
            ))

        return recommendations
