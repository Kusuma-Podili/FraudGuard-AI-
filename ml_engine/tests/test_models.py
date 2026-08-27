"""Unit tests for ML classifiers, Anomaly Detectors, and Meta-Ensemble."""

import unittest
import numpy as np

from ml_engine.models.xgboost_model import XGBoostFraudClassifier
from ml_engine.models.lightgbm_model import LightGBMFraudClassifier
from ml_engine.models.catboost_model import CatBoostFraudClassifier
from ml_engine.models.random_forest_model import BalancedRandomForestClassifier
from ml_engine.models.autoencoder_model import DeepAutoencoderAnomalyDetector
from ml_engine.models.isolation_forest_model import IsolationForestAnomalyDetector
from ml_engine.models.ensemble_pipeline import EnsemblePipeline


class TestMLModels(unittest.TestCase):

    def setUp(self):
        np.random.seed(42)
        # Synthetic feature matrix (100 samples, 8 features)
        self.X = np.random.randn(100, 8).astype(np.float32)
        self.y = np.zeros(100, dtype=np.int32)
        self.y[np.random.choice(100, 15, replace=False)] = 1  # 15% fraud

    def test_xgboost_fit_predict(self):
        clf = XGBoostFraudClassifier(n_estimators=5, max_depth=3)
        clf.fit(self.X, self.y)
        self.assertTrue(clf.is_trained)
        probs = clf.predict_proba(self.X)
        self.assertEqual(probs.shape, (100, 2))
        self.assertTrue(np.all((probs >= 0.0) & (probs <= 1.0)))

    def test_lightgbm_fit_predict(self):
        clf = LightGBMFraudClassifier(n_estimators=5, num_leaves=8)
        clf.fit(self.X, self.y)
        self.assertTrue(clf.is_trained)
        probs = clf.predict_proba(self.X)
        self.assertEqual(probs.shape, (100, 2))

    def test_catboost_fit_predict(self):
        clf = CatBoostFraudClassifier(n_estimators=5, depth=3)
        clf.fit(self.X, self.y)
        self.assertTrue(clf.is_trained)
        probs = clf.predict_proba(self.X)
        self.assertEqual(probs.shape, (100, 2))

    def test_autoencoder_anomaly_detection(self):
        ae = DeepAutoencoderAnomalyDetector(epochs=10, batch_size=32)
        ae.fit(self.X, self.y)
        self.assertTrue(ae.is_trained)
        probs = ae.predict_proba(self.X)
        self.assertEqual(probs.shape, (100, 2))

    def test_isolation_forest_anomaly_detection(self):
        iforest = IsolationForestAnomalyDetector(n_estimators=10)
        iforest.fit(self.X)
        self.assertTrue(iforest.is_trained)
        probs = iforest.predict_proba(self.X)
        self.assertEqual(probs.shape, (100, 2))

    def test_ensemble_pipeline_scoring(self):
        ens = EnsemblePipeline()
        ens.fit(self.X, self.y)
        pred = ens.score_transaction(self.X[0], card_id="CARD_123", device_id="DEV_999")
        self.assertIn(pred.decision_action, ["ALLOW", "REVIEW", "CHALLENGE_3DS", "DECLINE"])
        self.assertIn(pred.risk_tier, ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        self.assertGreaterEqual(pred.overall_fraud_score, 0.0)
        self.assertLessEqual(pred.overall_fraud_score, 1.0)


if __name__ == "__main__":
    unittest.main()
