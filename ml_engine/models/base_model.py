"""Abstract Base Model Definition, Evaluation Contracts, and Performance Metrics."""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import time
from typing import Dict, Any, List, Optional, Tuple
import numpy as np


@dataclass
class ModelEvaluationMetrics:
    """Standardized performance metrics container for fraud evaluation."""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    roc_auc: float = 0.0
    pr_auc: float = 0.0
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0
    avg_inference_latency_ms: float = 0.0
    p99_inference_latency_ms: float = 0.0
    optimal_threshold: float = 0.50
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accuracy": round(self.accuracy, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1_score": round(self.f1_score, 4),
            "roc_auc": round(self.roc_auc, 4),
            "pr_auc": round(self.pr_auc, 4),
            "false_positive_rate": round(self.false_positive_rate, 4),
            "false_negative_rate": round(self.false_negative_rate, 4),
            "avg_inference_latency_ms": round(self.avg_inference_latency_ms, 3),
            "p99_inference_latency_ms": round(self.p99_inference_latency_ms, 3),
            "optimal_threshold": round(self.optimal_threshold, 4),
            "evaluated_at": self.evaluated_at,
        }


@dataclass
class ModelMetadata:
    """Model governance metadata for registry tracking."""
    model_id: str
    model_name: str
    model_type: str
    version: str
    feature_names: List[str] = field(default_factory=list)
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    training_sample_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "CANDIDATE"  # CANDIDATE, CHAMPION, CHALLENGER, RETIRED


class BaseModel(ABC):
    """Abstract Base Class for all Fraud Detection classifiers."""

    def __init__(self, model_name: str, version: str = "1.0.0"):
        self.model_name = model_name
        self.version = version
        self.model_id = f"{model_name}_{version}".lower().replace(" ", "_")
        self.is_trained: bool = False
        self.threshold: float = 0.50
        self.feature_names: List[str] = []
        self.metadata = ModelMetadata(
            model_id=self.model_id,
            model_name=self.model_name,
            model_type=self.__class__.__name__,
            version=self.version
        )

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray, **kwargs) -> "BaseModel":
        """Train the model on feature matrix X and labels y."""
        raise NotImplementedError

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict fraud probability array of shape (N, 2) or (N,)."""
        raise NotImplementedError

    def predict(self, X: np.ndarray, threshold: Optional[float] = None) -> np.ndarray:
        """Predict binary classification (0: Legitimate, 1: Fraud)."""
        thr = self.threshold if threshold is None else threshold
        probs = self.predict_proba(X)
        if probs.ndim == 2:
            fraud_probs = probs[:, 1]
        else:
            fraud_probs = probs
        return (fraud_probs >= thr).astype(int)

    def get_feature_importances(self) -> Dict[str, float]:
        """Return dictionary mapping feature name to normalized importance score."""
        if not self.feature_names:
            return {}
        # Default uniform weights if not overridden by subclass
        val = 1.0 / len(self.feature_names)
        return {feat: round(val, 4) for feat in self.feature_names}

    def evaluate(self, X: np.ndarray, y_true: np.ndarray) -> ModelEvaluationMetrics:
        """Compute complete metric suite on validation data."""
        start_time = time.perf_counter()
        latencies = []

        # Benchmark single-sample latencies for first 100 samples
        n_benchmark = min(100, len(X))
        for i in range(n_benchmark):
            s = time.perf_counter()
            _ = self.predict_proba(X[i : i + 1])
            latencies.append((time.perf_counter() - s) * 1000.0)

        # Batch probability prediction
        probs = self.predict_proba(X)
        if probs.ndim == 2:
            p1 = probs[:, 1]
        else:
            p1 = probs

        y_pred = (p1 >= self.threshold).astype(int)

        # Calculate Confusion Matrix terms
        tp = int(np.sum((y_true == 1) & (y_pred == 1)))
        tn = int(np.sum((y_true == 0) & (y_pred == 0)))
        fp = int(np.sum((y_true == 0) & (y_pred == 1)))
        fn = int(np.sum((y_true == 1) & (y_pred == 0)))

        acc = (tp + tn) / max(len(y_true), 1)
        prec = tp / max(tp + fp, 1)
        rec = tp / max(tp + fn, 1)
        f1 = (2 * prec * rec) / max(prec + rec, 1e-8)
        fpr = fp / max(fp + tn, 1)
        fnr = fn / max(fn + tp, 1)

        # Calculate ROC-AUC & PR-AUC approximation
        roc_auc = self._calculate_roc_auc(y_true, p1)
        pr_auc = self._calculate_pr_auc(y_true, p1)

        avg_lat = float(np.mean(latencies)) if latencies else 1.0
        p99_lat = float(np.percentile(latencies, 99)) if latencies else 2.0

        optimal_thr = self.calibrate_threshold(y_true, p1)

        return ModelEvaluationMetrics(
            accuracy=acc,
            precision=prec,
            recall=rec,
            f1_score=f1,
            roc_auc=roc_auc,
            pr_auc=pr_auc,
            false_positive_rate=fpr,
            false_negative_rate=fnr,
            avg_inference_latency_ms=avg_lat,
            p99_inference_latency_ms=p99_lat,
            optimal_threshold=optimal_thr
        )

    def calibrate_threshold(self, y_true: np.ndarray, y_probs: np.ndarray) -> float:
        """Find decision threshold that maximizes the F1 score."""
        best_f1 = -1.0
        best_thr = 0.50

        for candidate in np.linspace(0.05, 0.95, 37):
            pred = (y_probs >= candidate).astype(int)
            tp = np.sum((y_true == 1) & (pred == 1))
            fp = np.sum((y_true == 0) & (pred == 1))
            fn = np.sum((y_true == 1) & (pred == 0))
            if tp + fp == 0 or tp + fn == 0:
                continue
            prec = tp / (tp + fp)
            rec = tp / (tp + fn)
            f1 = (2 * prec * rec) / max(prec + rec, 1e-8)
            if f1 > best_f1:
                best_f1 = f1
                best_thr = float(candidate)

        self.threshold = best_thr
        return best_thr

    def _calculate_roc_auc(self, y_true: np.ndarray, y_probs: np.ndarray) -> float:
        """Compute Mann-Whitney U test statistic equivalent for ROC-AUC."""
        pos_mask = (y_true == 1)
        neg_mask = (y_true == 0)
        n_pos = np.sum(pos_mask)
        n_neg = np.sum(neg_mask)
        if n_pos == 0 or n_neg == 0:
            return 0.5

        pos_scores = y_probs[pos_mask]
        neg_scores = y_probs[neg_mask]

        # Calculate rank sum
        all_scores = np.concatenate([pos_scores, neg_scores])
        ranks = np.argsort(np.argsort(all_scores)) + 1
        pos_rank_sum = np.sum(ranks[:n_pos])

        u_stat = pos_rank_sum - (n_pos * (n_pos + 1)) / 2.0
        auc = u_stat / (n_pos * n_neg)
        return float(np.clip(auc, 0.0, 1.0))

    def _calculate_pr_auc(self, y_true: np.ndarray, y_probs: np.ndarray) -> float:
        """Compute Average Precision / PR-AUC area."""
        sorted_indices = np.argsort(-y_probs)
        y_sorted = y_true[sorted_indices]
        tp_cumsum = np.cumsum(y_sorted == 1)
        fp_cumsum = np.cumsum(y_sorted == 0)

        n_pos = np.sum(y_true == 1)
        if n_pos == 0:
            return 0.0

        recalls = tp_cumsum / n_pos
        precisions = tp_cumsum / (tp_cumsum + fp_cumsum)

        # Trapezoidal numerical integration
        recalls = np.insert(recalls, 0, 0.0)
        precisions = np.insert(precisions, 0, 1.0)
        pr_auc = np.sum((recalls[1:] - recalls[:-1]) * precisions[1:])
        return float(np.clip(pr_auc, 0.0, 1.0))
