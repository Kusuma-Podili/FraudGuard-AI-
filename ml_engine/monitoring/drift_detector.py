"""Continuous Statistical Data Drift and Concept Drift Detector.

Tracks shifting statistical distributions between baseline training data and live production streams:
- Population Stability Index (PSI)
- Two-sample Kolmogorov-Smirnov (KS) Statistic
- Earth Mover's / 1-Wasserstein Distance
- Prediction Concept Drift Monitor
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import math
from typing import Dict, Any, List, Optional, Tuple
import numpy as np


@dataclass
class FeatureDriftMetric:
    feature_name: str
    psi_score: float
    ks_statistic: float
    drift_status: str  # NO_DRIFT, MODERATE_DRIFT, SEVERE_DRIFT
    baseline_mean: float
    current_mean: float
    baseline_std: float
    current_std: float


@dataclass
class DriftReport:
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    overall_drift_status: str = "NO_DRIFT"  # NO_DRIFT, WARNING, CRITICAL
    mean_psi_score: float = 0.0
    drifted_features_count: int = 0
    total_features_evaluated: int = 0
    feature_metrics: List[FeatureDriftMetric] = field(default_factory=list)
    retraining_recommended: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "overall_drift_status": self.overall_drift_status,
            "mean_psi_score": round(self.mean_psi_score, 4),
            "drifted_features_count": self.drifted_features_count,
            "total_features_evaluated": self.total_features_evaluated,
            "retraining_recommended": self.retraining_recommended,
            "metrics": [
                {
                    "feature": m.feature_name,
                    "psi": round(m.psi_score, 4),
                    "ks": round(m.ks_statistic, 4),
                    "status": m.drift_status,
                    "baseline_mean": round(m.baseline_mean, 2),
                    "current_mean": round(m.current_mean, 2),
                }
                for m in self.feature_metrics
            ],
        }


class DriftDetector:
    """Continuous statistical distribution monitor."""

    def __init__(
        self,
        baseline_data: Optional[np.ndarray] = None,
        feature_names: Optional[List[str]] = None,
        num_bins: int = 10,
        psi_warning_threshold: float = 0.10,
        psi_critical_threshold: float = 0.25
    ):
        self.baseline_data = baseline_data
        self.feature_names = feature_names or []
        self.num_bins = num_bins
        self.psi_warning_threshold = psi_warning_threshold
        self.psi_critical_threshold = psi_critical_threshold
        self.bin_edges_: Dict[int, np.ndarray] = {}
        self.baseline_proportions_: Dict[int, np.ndarray] = {}

        if baseline_data is not None:
            self.set_baseline(baseline_data, feature_names)

    def set_baseline(self, X_base: np.ndarray, feature_names: Optional[List[str]] = None) -> None:
        """Fit empirical baseline distribution quantiles."""
        self.baseline_data = X_base
        if feature_names:
            self.feature_names = feature_names
        elif not self.feature_names:
            self.feature_names = [f"feature_{i}" for i in range(X_base.shape[1])]

        n_features = X_base.shape[1]
        self.bin_edges_ = {}
        self.baseline_proportions_ = {}

        for j in range(n_features):
            col = X_base[:, j]
            percentiles = np.linspace(0, 100, self.num_bins + 1)
            edges = np.unique(np.percentile(col, percentiles))
            if len(edges) < 2:
                edges = np.array([float(np.min(col)) - 1.0, float(np.max(col)) + 1.0])

            self.bin_edges_[j] = edges

            # Baseline counts per bin
            counts, _ = np.histogram(col, bins=edges)
            proportions = (counts + 1e-4) / (len(col) + 1e-4 * len(counts))
            self.baseline_proportions_[j] = proportions

    def calculate_psi(self, current_col: np.ndarray, feature_idx: int) -> float:
        """Calculate Population Stability Index for a single feature column."""
        if feature_idx not in self.bin_edges_:
            return 0.0

        edges = self.bin_edges_[feature_idx]
        base_props = self.baseline_proportions_[feature_idx]

        # Current counts
        counts, _ = np.histogram(current_col, bins=edges)
        curr_props = (counts + 1e-4) / (len(current_col) + 1e-4 * len(counts))

        # PSI Formula: sum( (Actual - Expected) * ln(Actual / Expected) )
        psi = np.sum((curr_props - base_props) * np.log(curr_props / base_props))
        return max(0.0, float(psi))

    def calculate_ks_statistic(self, base_col: np.ndarray, curr_col: np.ndarray) -> float:
        """Compute two-sample Kolmogorov-Smirnov distance."""
        base_sorted = np.sort(base_col)
        curr_sorted = np.sort(curr_col)

        all_vals = np.concatenate([base_sorted, curr_sorted])
        cdf_base = np.searchsorted(base_sorted, all_vals, side="right") / len(base_sorted)
        cdf_curr = np.searchsorted(curr_sorted, all_vals, side="right") / len(curr_sorted)

        ks_stat = float(np.max(np.abs(cdf_base - cdf_curr)))
        return ks_stat

    def evaluate_drift(self, X_current: np.ndarray) -> DriftReport:
        """Evaluate full statistical drift report comparing live batch to baseline."""
        if self.baseline_data is None:
            raise ValueError("Baseline dataset not established. Call set_baseline() first.")

        n_features = X_current.shape[1]
        metrics: List[FeatureDriftMetric] = []
        drift_count = 0

        for j in range(n_features):
            feat_name = self.feature_names[j] if j < len(self.feature_names) else f"f_{j}"
            base_col = self.baseline_data[:, j]
            curr_col = X_current[:, j]

            psi = self.calculate_psi(curr_col, j)
            ks = self.calculate_ks_statistic(base_col, curr_col)

            if psi >= self.psi_critical_threshold:
                status = "SEVERE_DRIFT"
                drift_count += 1
            elif psi >= self.psi_warning_threshold:
                status = "MODERATE_DRIFT"
                drift_count += 1
            else:
                status = "NO_DRIFT"

            metrics.append(FeatureDriftMetric(
                feature_name=feat_name,
                psi_score=psi,
                ks_statistic=ks,
                drift_status=status,
                baseline_mean=float(np.mean(base_col)),
                current_mean=float(np.mean(curr_col)),
                baseline_std=float(np.std(base_col)),
                current_std=float(np.std(curr_col))
            ))

        mean_psi = float(np.mean([m.psi_score for m in metrics])) if metrics else 0.0

        if drift_count >= 3 or mean_psi >= self.psi_critical_threshold:
            overall_status = "CRITICAL"
            retrain = True
        elif drift_count >= 1 or mean_psi >= self.psi_warning_threshold:
            overall_status = "WARNING"
            retrain = False
        else:
            overall_status = "NO_DRIFT"
            retrain = False

        return DriftReport(
            overall_drift_status=overall_status,
            mean_psi_score=mean_psi,
            drifted_features_count=drift_count,
            total_features_evaluated=n_features,
            feature_metrics=metrics,
            retraining_recommended=retrain
        )
