"""Real-Time Fraud Decision Engine (<20ms SLA).

Combines Feature Store enrichment, AST Business Rules, and Multi-Model ML Ensemble
to generate definitive real-time authorization actions (ALLOW, REVIEW, CHALLENGE_3DS, DECLINE).
"""

from __future__ import annotations
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from ml_engine.data.feature_store import get_feature_store, FeatureStore
from ml_engine.models.ensemble_pipeline import get_default_ensemble, EnsemblePipeline, EnsemblePrediction
from backend.app.services.rule_evaluator import SafeRuleEvaluator
from backend.app.core.config import settings
from backend.app.core.logging import get_logger

logger = get_logger("fraudguard.decision_engine")


class DecisionEngine:
    """Sub-20ms real-time orchestration engine."""

    def __init__(
        self,
        feature_store: Optional[FeatureStore] = None,
        ensemble: Optional[EnsemblePipeline] = None
    ):
        self.feature_store = feature_store or get_feature_store()
        self.ensemble = ensemble or get_default_ensemble()

        # In-memory active rules cache for zero-latency lookup
        self._active_rules: List[Dict[str, Any]] = self._init_default_rules()

    def _init_default_rules(self) -> List[Dict[str, Any]]:
        """Default cached rules."""
        return [
            {
                "rule_code": "RULE_PIN_004",
                "name": "Failed PIN Credential Brute Force",
                "condition": "failed_pin_attempts_24h >= 3",
                "action": "DECLINE",
                "priority": 1,
            },
            {
                "rule_code": "RULE_GEO_002",
                "name": "Impossible Travel Teleportation",
                "condition": "is_impossible_travel == True OR travel_velocity_kmh > 950.0",
                "action": "DECLINE",
                "priority": 5,
            },
            {
                "rule_code": "RULE_VEL_001",
                "name": "Rapid Burst Velocity Limit",
                "condition": "velocity_1h >= 4",
                "action": "CHALLENGE_3DS",
                "priority": 10,
            },
            {
                "rule_code": "RULE_AMT_003",
                "name": "Extreme High-Ticket Outlier",
                "condition": "amount >= 4000.0 AND amount_ratio_to_mean_30d > 5.0",
                "action": "REVIEW",
                "priority": 20,
            },
        ]

    def update_rules_cache(self, rules: List[Dict[str, Any]]) -> None:
        """Hot-reload active rules in memory without restart."""
        self._active_rules = sorted(rules, key=lambda r: r.get("priority", 100))

    def evaluate_transaction(self, raw_tx: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete real-time evaluation pipeline with latency timing."""
        start_time = time.perf_counter()
        tx_id = raw_tx.get("transaction_id") or f"TX_{uuid.uuid4().hex[:12].upper()}"
        card_id = str(raw_tx.get("card_id", "CARD_UNKNOWN"))
        device_id = str(raw_tx.get("device_fingerprint", ""))
        ip_addr = str(raw_tx.get("ip_address", ""))

        # 1. Feature Store Enrichment (Online velocity, geodistance, entity profiles)
        enriched = self.feature_store.enrich_transaction(raw_tx)
        enriched["transaction_id"] = tx_id

        # 2. Dynamic AST Business Rule Evaluation
        triggered_rules = []
        rule_overridden_action = None

        for rule in self._active_rules:
            try:
                is_match, _ = SafeRuleEvaluator.evaluate_expression(rule["condition"], enriched)
                if is_match:
                    triggered_rules.append({
                        "rule_code": rule["rule_code"],
                        "name": rule["name"],
                        "action": rule["action"],
                    })
                    # First matched high-priority hard rule dictates action if DECLINE or CHALLENGE
                    if rule_overridden_action is None and rule["action"] in ("DECLINE", "CHALLENGE_3DS"):
                        rule_overridden_action = rule["action"]
            except Exception as err:
                logger.warning(f"Error evaluating rule {rule.get('rule_code')}: {err}")

        # 3. Machine Learning Multi-Model Ensemble Scoring
        feat_vec = self.feature_store.get_feature_vector(enriched)
        ml_prediction: EnsemblePrediction = self.ensemble.score_transaction(
            feature_vector=feat_vec,
            card_id=card_id,
            device_id=device_id,
            ip_address=ip_addr
        )

        # 4. Arbitration Strategy (Deterministic Rule vs ML Ensemble)
        final_action = ml_prediction.decision_action
        final_score = ml_prediction.overall_fraud_score

        if rule_overridden_action is not None:
            final_action = rule_overridden_action
            if final_action == "DECLINE":
                final_score = max(final_score, 0.95)
            elif final_action == "CHALLENGE_3DS":
                final_score = max(final_score, 0.75)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "transaction_id": tx_id,
            "decision_action": final_action,
            "risk_score": round(final_score, 4),
            "risk_tier": ml_prediction.risk_tier if not rule_overridden_action else ("CRITICAL" if final_action == "DECLINE" else "HIGH"),
            "confidence_level": ml_prediction.confidence_level,
            "triggered_rules": triggered_rules,
            "model_breakdown": ml_prediction.model_breakdown,
            "is_anomaly": ml_prediction.anomaly_flag,
            "is_impossible_travel": bool(enriched.get("is_impossible_travel", False)),
            "requires_step_up_auth": (final_action == "CHALLENGE_3DS"),
            "latency_ms": round(elapsed_ms, 2),
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "enriched_features": enriched,
        }


# Singleton decision engine
_GLOBAL_DECISION_ENGINE: Optional[DecisionEngine] = None


def get_decision_engine() -> DecisionEngine:
    """Retrieve singleton decision engine."""
    global _GLOBAL_DECISION_ENGINE
    if _GLOBAL_DECISION_ENGINE is None:
        _GLOBAL_DECISION_ENGINE = DecisionEngine()
    return _GLOBAL_DECISION_ENGINE
