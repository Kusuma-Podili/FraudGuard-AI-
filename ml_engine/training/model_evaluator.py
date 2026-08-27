"""Stratified K-Fold Cross Validation and Model Comparison Suite."""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple, Type
import numpy as np

from ml_engine.models.base_model import BaseModel, ModelEvaluationMetrics


class StratifiedCrossValidator:
    """Stratified K-Fold cross validator preserving minority fraud class ratios."""

    def __init__(self, n_splits: int = 5, shuffle: bool = True, random_state: int = 42):
        self.n_splits = n_splits
        self.shuffle = shuffle
        self.random_state = random_state

    def split(self, X: np.ndarray, y: np.ndarray) -> List[Tuple[np.ndarray, np.ndarray]]:
        """Generate stratified train/validation index pairs."""
        rng = np.random.default_rng(self.random_state)
        pos_idx = np.where(y == 1)[0]
        neg_idx = np.where(y == 0)[0]

        if self.shuffle:
            rng.shuffle(pos_idx)
            rng.shuffle(neg_idx)

        pos_folds = np.array_split(pos_idx, self.n_splits)
        neg_folds = np.array_split(neg_idx, self.n_splits)

        splits = []
        for i in range(self.n_splits):
            val_idx = np.concatenate([pos_folds[i], neg_folds[i]])
            train_idx = np.concatenate([
                np.concatenate([pos_folds[j] for j in range(self.n_splits) if j != i]),
                np.concatenate([neg_folds[j] for j in range(self.n_splits) if j != i])
            ])
            splits.append((train_idx, val_idx))

        return splits

    def cross_validate(
        self,
        model_factory: Type[BaseModel],
        X: np.ndarray,
        y: np.ndarray,
        feature_names: Optional[List[str]] = None,
        **model_kwargs
    ) -> Dict[str, Any]:
        """Run complete K-fold cross-validation and return mean and std metrics."""
        splits = self.split(X, y)
        fold_metrics: List[ModelEvaluationMetrics] = []

        for fold_num, (train_idx, val_idx) in enumerate(splits):
            model = model_factory(**model_kwargs)
            model.fit(X[train_idx], y[train_idx], feature_names=feature_names)
            metrics = model.evaluate(X[val_idx], y[val_idx])
            fold_metrics.append(metrics)

        return {
            "n_folds": self.n_splits,
            "mean_roc_auc": round(float(np.mean([m.roc_auc for m in fold_metrics])), 4),
            "std_roc_auc": round(float(np.std([m.roc_auc for m in fold_metrics])), 4),
            "mean_pr_auc": round(float(np.mean([m.pr_auc for m in fold_metrics])), 4),
            "mean_precision": round(float(np.mean([m.precision for m in fold_metrics])), 4),
            "mean_recall": round(float(np.mean([m.recall for m in fold_metrics])), 4),
            "mean_f1": round(float(np.mean([m.f1_score for m in fold_metrics])), 4),
            "mean_p99_latency_ms": round(float(np.mean([m.p99_inference_latency_ms for m in fold_metrics])), 3),
        }
