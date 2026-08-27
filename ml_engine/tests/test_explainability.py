"""Unit tests for SHAP, LIME, and Counterfactual explainability."""

import unittest
import numpy as np

from ml_engine.models.xgboost_model import XGBoostFraudClassifier
from ml_engine.explainability.shap_explainer import ShapExplainer
from ml_engine.explainability.lime_explainer import LimeExplainer
from ml_engine.explainability.counterfactual import CounterfactualExplainer


class TestExplainability(unittest.TestCase):

    def setUp(self):
        np.random.seed(42)
        self.feature_names = ["amount", "age", "distance", "velocity_1h"]
        self.X = np.random.randn(80, 4).astype(np.float32)
        self.y = np.random.randint(0, 2, size=80)
        self.model = XGBoostFraudClassifier(n_estimators=5, max_depth=3)
        self.model.fit(self.X, self.y, feature_names=self.feature_names)

    def test_shap_waterfall_explanation(self):
        explainer = ShapExplainer(self.model, feature_names=self.feature_names)
        res = explainer.explain_transaction(self.X[0])
        self.assertIsNotNone(res.output_score)
        self.assertEqual(len(res.features), 4)
        waterfall_dict = res.to_dict()
        self.assertIn("waterfall", waterfall_dict)
        self.assertIn("top_risk_factors", waterfall_dict)

    def test_lime_local_surrogate(self):
        lime = LimeExplainer(self.model, num_samples=50)
        res = lime.explain_instance(self.X[0], feature_names=self.feature_names)
        self.assertIn("top_features", res)
        self.assertGreater(len(res["top_features"]), 0)

    def test_counterfactual_recommendations(self):
        cf = CounterfactualExplainer(self.model)
        raw_tx = {
            "amount": 2500.0,
            "failed_pin_attempts_24h": 3,
            "distance_from_home_km": 1200.0,
            "entry_mode": "CNP"
        }
        recs = cf.generate_counterfactual(raw_tx, current_score=0.85, feature_vector=self.X[0])
        self.assertGreater(len(recs), 0)
        self.assertTrue(any(r.feature_name == "amount" for r in recs))


if __name__ == "__main__":
    unittest.main()
