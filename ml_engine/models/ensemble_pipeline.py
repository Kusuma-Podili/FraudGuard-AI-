"""Unified Meta-Ensemble Stacking Pipeline for Real-Time Fraud Classification.

Combines heterogeneous model families:
1. Tree Ensembles: XGBoost, LightGBM, CatBoost, Balanced Random Forest
2. Unsupervised Anomaly Detectors: Deep Autoencoders, Isolation Forests
3. Graph Topology Detectors: Multi-entity syndicate detector

Computes meta-probability calibration and outputs automated decision actions
(ALLOW, REVIEW, CHALLENGE_3DS, DECLINE).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from ml_engine.models.base_model import BaseModel, ModelEvaluationMetrics
from ml_engine.models.xgboost_model import XGBoostFraudClassifier
from ml_engine.models.lightgbm_model import LightGBMFraudClassifier
from ml_engine.models.catboost_model import CatBoostFraudClassifier
from ml_engine.models.random_forest_model import BalancedRandomForestClassifier
from ml_engine.models.autoencoder_model import DeepAutoencoderAnomalyDetector
from ml_engine.models.isolation_forest_model import IsolationForestAnomalyDetector
from ml_engine.models.graph_detector import FraudGraphNetworkDetector


@dataclass
class EnsemblePrediction:
    """Detailed score payload returned by the ensemble engine."""
    overall_fraud_score: float
    decision_action: str  # ALLOW, REVIEW, CHALLENGE_3DS, DECLINE
    confidence_level: str # LOW, MEDIUM, HIGH, VERY_HIGH
    model_breakdown: Dict[str, float]
    anomaly_flag: bool
    graph_syndicate_flag: bool
    risk_tier: str       # LOW, MEDIUM, HIGH, CRITICAL


class EnsemblePipeline(BaseModel):
    """Production Meta-Ensemble Pipeline combining 6 ML models and graph network detector."""

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        review_threshold: float = 0.30,
        challenge_threshold: float = 0.65,
        decline_threshold: float = 0.85,
        version: str = "3.1.0"
    ):
        super().__init__(model_name="Meta_Ensemble_Fraud_Guard", version=version)
        self.review_threshold = review_threshold
        self.challenge_threshold = challenge_threshold
        self.decline_threshold = decline_threshold

        # Default weighted probability contributions
        self.weights = weights or {
            "xgboost": 0.35,
            "lightgbm": 0.25,
            "catboost": 0.20,
            "random_forest": 0.10,
            "autoencoder": 0.05,
            "isolation_forest": 0.05,
        }

        # Normalize weights to sum to 1.0
        total_w = sum(self.weights.values())
        self.weights = {k: v / total_w for k, v in self.weights.items()}

        # Instantiate sub-models
        self.xgb = XGBoostFraudClassifier()
        self.lgbm = LightGBMFraudClassifier()
        self.catboost = CatBoostFraudClassifier()
        self.rf = BalancedRandomForestClassifier()
        self.autoencoder = DeepAutoencoderAnomalyDetector()
        self.iforest = IsolationForestAnomalyDetector()
        self.graph_detector = FraudGraphNetworkDetector()

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None, **kwargs) -> "EnsemblePipeline":
        """Fit all constituent base models."""
        if feature_names:
            self.feature_names = feature_names

        self.xgb.fit(X, y, feature_names=feature_names)
        self.lgbm.fit(X, y, feature_names=feature_names)
        self.catboost.fit(X, y, feature_names=feature_names)
        self.rf.fit(X, y, feature_names=feature_names)
        self.autoencoder.fit(X, y, feature_names=feature_names)
        self.iforest.fit(X, y, feature_names=feature_names)

        self.is_trained = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Compute weighted probability combination."""
        p_xgb = self.xgb.predict_proba(X)[:, 1]
        p_lgbm = self.lgbm.predict_proba(X)[:, 1]
        p_cat = self.catboost.predict_proba(X)[:, 1]
        p_rf = self.rf.predict_proba(X)[:, 1]
        p_ae = self.autoencoder.predict_proba(X)[:, 1]
        p_if = self.iforest.predict_proba(X)[:, 1]

        ensemble_p1 = (
            self.weights["xgboost"] * p_xgb
            + self.weights["lightgbm"] * p_lgbm
            + self.weights["catboost"] * p_cat
            + self.weights["random_forest"] * p_rf
            + self.weights["autoencoder"] * p_ae
            + self.weights["isolation_forest"] * p_if
        )

        return np.column_stack([1.0 - ensemble_p1, ensemble_p1])

    def score_transaction(
        self,
        feature_vector: np.ndarray,
        card_id: str = "",
        device_id: str = "",
        ip_address: str = ""
    ) -> EnsemblePrediction:
        """Evaluate a single transaction with complete telemetry and action routing."""
        X_single = feature_vector.reshape(1, -1)

        # Predict probabilities across base models
        p_xgb = float(self.xgb.predict_proba(X_single)[0, 1])
        p_lgbm = float(self.lgbm.predict_proba(X_single)[0, 1])
        p_cat = float(self.catboost.predict_proba(X_single)[0, 1])
        p_rf = float(self.rf.predict_proba(X_single)[0, 1])
        p_ae = float(self.autoencoder.predict_proba(X_single)[0, 1])
        p_if = float(self.iforest.predict_proba(X_single)[0, 1])

        # Graph ring detection
        graph_risk, graph_telemetry = self.graph_detector.compute_ring_risk_score(
            card_id=card_id, device_id=device_id, ip_address=ip_address
        )
        self.graph_detector.add_edge(card_id=card_id, device_id=device_id, ip_address=ip_address)

        # Weighted score
        base_score = (
            self.weights["xgboost"] * p_xgb
            + self.weights["lightgbm"] * p_lgbm
            + self.weights["catboost"] * p_cat
            + self.weights["random_forest"] * p_rf
            + self.weights["autoencoder"] * p_ae
            + self.weights["isolation_forest"] * p_if
        )

        # Amplify with graph syndicate signal if detected
        final_score = float(np.clip(max(base_score, graph_risk * 0.90), 0.0, 1.0))

        # Determine Action
        if final_score >= self.decline_threshold:
            action = "DECLINE"
            risk_tier = "CRITICAL"
        elif final_score >= self.challenge_threshold:
            action = "CHALLENGE_3DS"
            risk_tier = "HIGH"
        elif final_score >= self.review_threshold:
            action = "REVIEW"
            risk_tier = "MEDIUM"
        else:
            action = "ALLOW"
            risk_tier = "LOW"

        # Model variance for confidence
        model_scores = [p_xgb, p_lgbm, p_cat, p_rf, p_ae, p_if]
        score_std = float(np.std(model_scores))
        confidence = "VERY_HIGH" if score_std < 0.08 else "HIGH" if score_std < 0.15 else "MEDIUM"

        return EnsemblePrediction(
            overall_fraud_score=round(final_score, 4),
            decision_action=action,
            confidence_level=confidence,
            model_breakdown={
                "xgboost": round(p_xgb, 4),
                "lightgbm": round(p_lgbm, 4),
                "catboost": round(p_cat, 4),
                "random_forest": round(p_rf, 4),
                "autoencoder": round(p_ae, 4),
                "isolation_forest": round(p_if, 4),
                "graph_syndicate": round(graph_risk, 4),
            },
            anomaly_flag=(p_ae > 0.70 or p_if > 0.70),
            graph_syndicate_flag=graph_telemetry["is_potential_fraud_ring"],
            risk_tier=risk_tier
        )


# Singleton factory
_GLOBAL_ENSEMBLE: Optional[EnsemblePipeline] = None


def get_default_ensemble() -> EnsemblePipeline:
    """Retrieve or initialize the global trained ensemble pipeline."""
    global _GLOBAL_ENSEMBLE
    if _GLOBAL_ENSEMBLE is None:
        _GLOBAL_ENSEMBLE = EnsemblePipeline()
    return _GLOBAL_ENSEMBLE
