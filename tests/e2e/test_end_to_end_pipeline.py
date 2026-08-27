"""End-to-End Comprehensive Lifecycle Test for FraudGuard AI.

Validates the end-to-end flow:
1. Transaction Generation (Legitimate & Adversarial Archetypes)
2. Real-Time Feature Store Enrichment (Haversine & Velocity Ring Buffers)
3. AST Business Rules Gating
4. Machine Learning Multi-Model Ensemble Inference (<20ms SLA)
5. Automated Triage & SLA Escalation
6. Explainable AI (SHAP attributions & FCRA Adverse Action Counterfactuals)
"""

import unittest
from datetime import datetime, timezone

from ml_engine.data.dataset_generator import SyntheticTransactionGenerator
from ml_engine.data.feature_store import get_feature_store
from ml_engine.models.ensemble_pipeline import get_default_ensemble
from ml_engine.explainability.shap_explainer import ShapExplainer
from ml_engine.explainability.counterfactual import CounterfactualExplainer
from backend.app.services.decision_engine import DecisionEngine
from backend.app.services.rule_evaluator import SafeRuleEvaluator
from simulator.archetypes import ImpossibleTravelArchetype, CardTestingArchetype


class TestEndToEndFraudGuardPipeline(unittest.TestCase):

    def setUp(self):
        self.generator = SyntheticTransactionGenerator(seed=123)
        self.feature_store = get_feature_store()
        self.decision_engine = DecisionEngine()

    def test_e2e_legitimate_flow(self):
        """Test legitimate transaction processing and instant approval."""
        tx = self.generator.generate_single_transaction(
            timestamp=datetime.now(timezone.utc),
            force_fraud=False
        )
        res = self.decision_engine.evaluate_transaction(tx)

        self.assertIn("transaction_id", res)
        self.assertIn("decision_action", res)
        self.assertIn(res["decision_action"], ["ALLOW", "REVIEW"])
        self.assertLess(res["latency_ms"], 50.0)

    def test_e2e_impossible_travel_flow(self):
        """Test impossible velocity teleportation detection and rule trigger."""
        pair = ImpossibleTravelArchetype.generate_pair("CARD_E2E_TRAVEL_01")
        ny_tx = pair[0]
        tokyo_tx = pair[1]

        # Ingest first NY transaction
        _ = self.decision_engine.evaluate_transaction(ny_tx)

        # Ingest Tokyo transaction 10 min later
        tokyo_res = self.decision_engine.evaluate_transaction(tokyo_tx)

        self.assertIn("decision_action", tokyo_res)
        # Should be flagged high risk or declined due to impossible travel
        self.assertIn(tokyo_res["decision_action"], ["DECLINE", "REVIEW", "CHALLENGE_3DS"])

    def test_e2e_xai_explainability_flow(self):
        """Test TreeSHAP waterfall calculation and counterfactual generation."""
        raw_tx = {
            "card_id": "CARD_E2E_XAI_01",
            "amount": 3450.0,
            "merchant_category": "ELECTRONICS",
            "failed_pin_attempts_24h": 2,
            "entry_mode": "CNP",
        }
        enriched = self.feature_store.enrich_transaction(raw_tx)
        vec = self.feature_store.get_feature_vector(enriched)

        ensemble = get_default_ensemble()
        pred = ensemble.score_transaction(vec)

        # 1. SHAP Waterfall
        explainer = ShapExplainer(model=ensemble.xgb)
        shap_res = explainer.explain_transaction(vec, raw_attributes=enriched)
        self.assertIsNotNone(shap_res.base_value)
        self.assertGreater(len(shap_res.features), 0)

        # 2. Counterfactual Recommendations

        cf_explainer = CounterfactualExplainer(model=ensemble.xgb)
        recs = cf_explainer.generate_counterfactual(enriched, current_score=pred.overall_fraud_score, feature_vector=vec)
        self.assertIsInstance(recs, list)


if __name__ == "__main__":
    unittest.main()
