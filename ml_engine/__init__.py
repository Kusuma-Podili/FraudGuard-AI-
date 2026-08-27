"""FraudGuard AI: Machine Learning & MLOps Subsystem.

This package provides:
- Synthetic transaction generation with realistic fraud distributions
- Feature engineering, sliding-window velocity aggregation, and online/offline feature store
- Multi-model ensemble classifiers (XGBoost, LightGBM, CatBoost, Autoencoders, Isolation Forests)
- Explainable AI (SHAP, LIME, counterfactuals, surrogate rule extraction)
- Drift detection (PSI, KS-test, Wasserstein distance) and continuous model monitoring
- End-to-end training and automated hyperparameter optimization pipelines
"""

__version__ = "1.0.0"
__author__ = "FraudGuard AI Team"

from ml_engine.data.feature_store import FeatureStore, get_feature_store
from ml_engine.models.ensemble_pipeline import EnsemblePipeline, get_default_ensemble
from ml_engine.explainability.shap_explainer import ShapExplainer
from ml_engine.monitoring.drift_detector import DriftDetector

__all__ = [
    "FeatureStore",
    "get_feature_store",
    "EnsemblePipeline",
    "get_default_ensemble",
    "ShapExplainer",
    "DriftDetector",
]
