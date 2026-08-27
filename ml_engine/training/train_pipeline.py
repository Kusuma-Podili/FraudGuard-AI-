"""End-to-End Automated Multi-Model Training and Evaluation Pipeline.

Orchestrates data generation/ingestion, feature preprocessor calibration,
class imbalance resampling, individual model training, meta-ensemble blending,
and performance benchmarking.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from ml_engine.data.dataset_generator import SyntheticTransactionGenerator
from ml_engine.data.feature_store import FeatureStore, get_feature_store
from ml_engine.data.balance_handlers import SMOTEHandler
from ml_engine.models.ensemble_pipeline import EnsemblePipeline, get_default_ensemble
from ml_engine.models.base_model import ModelEvaluationMetrics
from ml_engine.training.cost_matrix import FinancialCostMatrix


@dataclass
class TrainingJobResult:
    job_id: str
    status: str
    training_sample_count: int
    validation_sample_count: int
    feature_count: int
    ensemble_metrics: Dict[str, Any]
    submodel_metrics: Dict[str, Dict[str, Any]]
    cost_evaluation: Dict[str, Any]
    completed_at: str


class TrainingPipeline:
    """Full production training pipeline runner."""

    def __init__(self, feature_store: Optional[FeatureStore] = None):
        self.feature_store = feature_store or get_feature_store()
        self.smote = SMOTEHandler(sampling_ratio=0.15)
        self.cost_matrix = FinancialCostMatrix()

    def run(self, n_samples: int = 4000, fraud_ratio: float = 0.03) -> Tuple[EnsemblePipeline, TrainingJobResult]:
        """Execute complete training workflow."""
        job_id = f"TRAIN_JOB_{int(datetime.now(timezone.utc).timestamp())}"

        # 1. Generate Synthetic Financial Transactions
        gen = SyntheticTransactionGenerator(seed=42)
        raw_dataset = gen.generate_dataset(n_samples=n_samples, fraud_ratio=fraud_ratio)

        # 2. Feature Enrichment via Feature Store
        enriched_records = [self.feature_store.enrich_transaction(r) for r in raw_dataset]
        labels = [int(r["is_fraud"]) for r in raw_dataset]
        amounts = np.array([float(r["amount"]) for r in raw_dataset])

        # 3. Fit Tabular Preprocessor
        self.feature_store.preprocessor.fit(enriched_records, labels)
        X_matrix = self.feature_store.preprocessor.transform_batch(enriched_records)
        y_vec = np.array(labels, dtype=np.int32)
        feature_names = self.feature_store.preprocessor.feature_names_out_

        # 4. Train/Validation Split (80% / 20% Stratified)
        pos_idx = np.where(y_vec == 1)[0]
        neg_idx = np.where(y_vec == 0)[0]

        train_pos = pos_idx[: int(0.8 * len(pos_idx))]
        val_pos = pos_idx[int(0.8 * len(pos_idx)) :]
        train_neg = neg_idx[: int(0.8 * len(neg_idx))]
        val_neg = neg_idx[int(0.8 * len(neg_idx)) :]

        train_idx = np.concatenate([train_pos, train_neg])
        val_idx = np.concatenate([val_pos, val_neg])

        X_train, y_train = X_matrix[train_idx], y_vec[train_idx]
        X_val, y_val = X_matrix[val_idx], y_vec[val_idx]
        val_amounts = amounts[val_idx]

        # 5. Apply SMOTE Resampling to Training Partition
        X_train_resampled, y_train_resampled = self.smote.fit_resample(X_train, y_train)

        # 6. Fit Meta-Ensemble and constituent base models
        ensemble = get_default_ensemble()
        ensemble.fit(X_train_resampled, y_train_resampled, feature_names=feature_names)

        # 7. Evaluate Sub-models & Meta-Ensemble
        submodel_metrics = {
            "xgboost": ensemble.xgb.evaluate(X_val, y_val).to_dict(),
            "lightgbm": ensemble.lgbm.evaluate(X_val, y_val).to_dict(),
            "catboost": ensemble.catboost.evaluate(X_val, y_val).to_dict(),
            "random_forest": ensemble.rf.evaluate(X_val, y_val).to_dict(),
            "autoencoder": ensemble.autoencoder.evaluate(X_val, y_val).to_dict(),
            "isolation_forest": ensemble.iforest.evaluate(X_val, y_val).to_dict(),
        }

        ensemble_eval = ensemble.evaluate(X_val, y_val)

        # 8. Financial Cost-Benefit Evaluation
        val_decisions = []
        for i in range(len(X_val)):
            pred = ensemble.score_transaction(X_val[i])
            val_decisions.append(pred.decision_action)

        cost_summary = self.cost_matrix.evaluate_financial_pnl(val_amounts, y_val, val_decisions)

        result = TrainingJobResult(
            job_id=job_id,
            status="SUCCESS",
            training_sample_count=len(X_train),
            validation_sample_count=len(X_val),
            feature_count=X_matrix.shape[1],
            ensemble_metrics=ensemble_eval.to_dict(),
            submodel_metrics=submodel_metrics,
            cost_evaluation=cost_summary.to_dict(),
            completed_at=datetime.now(timezone.utc).isoformat()
        )

        return ensemble, result


def run_training_job(n_samples: int = 3000) -> TrainingJobResult:
    """Convenience helper to run model training."""
    pipeline = TrainingPipeline()
    _, result = pipeline.run(n_samples=n_samples)
    return result
