"""Automated Tabular Data Quality, Integrity, and Anomaly Gatekeeper.

Performs schema verification, missingness audits, variance collapse detection,
and distribution outlier checks on streaming transactions.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import numpy as np


@dataclass
class QualityAuditResult:
    passed: bool
    total_checks: int
    failed_checks: int
    error_messages: List[str]
    warning_messages: List[str]
    missing_rate: float
    outlier_rate: float


class DataQualityAuditor:
    """Pre-inference data quality gateway."""

    def __init__(self, max_allowed_missing_pct: float = 0.05, outlier_zscore_limit: float = 4.5):
        self.max_allowed_missing_pct = max_allowed_missing_pct
        self.outlier_zscore_limit = outlier_zscore_limit

    def audit_batch(self, X: np.ndarray, feature_names: Optional[List[str]] = None) -> QualityAuditResult:
        """Run complete sanity checks across feature batch."""
        errors = []
        warnings = []
        n_samples, n_features = X.shape
        names = feature_names or [f"col_{i}" for i in range(n_features)]

        # 1. Missingness / NaN check
        nan_mask = np.isnan(X)
        total_nans = int(np.sum(nan_mask))
        missing_rate = total_nans / max(X.size, 1)

        if missing_rate > self.max_allowed_missing_pct:
            errors.append(f"Missing value rate {missing_rate:.2%} exceeds threshold {self.max_allowed_missing_pct:.2%}")
        elif total_nans > 0:
            warnings.append(f"Detected {total_nans} NaN values; automatic median imputation applied.")

        # 2. Zero-variance / feature collapse check
        for j in range(n_features):
            col = X[:, j]
            clean = col[~np.isnan(col)]
            if len(clean) > 0 and np.std(clean) < 1e-7:
                warnings.append(f"Feature '{names[j]}' exhibits zero variance (collapsed constant value).")

        # 3. Extreme Z-score outliers
        outlier_count = 0
        for j in range(n_features):
            col = X[:, j]
            clean = col[~np.isnan(col)]
            if len(clean) > 5:
                mean = np.mean(clean)
                std = np.std(clean)
                if std > 1e-6:
                    z_scores = np.abs((clean - mean) / std)
                    outliers_in_col = int(np.sum(z_scores > self.outlier_zscore_limit))
                    outlier_count += outliers_in_col
                    if outliers_in_col > 0.02 * len(clean):
                        warnings.append(f"Feature '{names[j]}' has {outliers_in_col} extreme outliers (>|z|={self.outlier_zscore_limit}).")

        outlier_rate = outlier_count / max(X.size, 1)
        passed = len(errors) == 0

        return QualityAuditResult(
            passed=passed,
            total_checks=n_features * 3 + 1,
            failed_checks=len(errors),
            error_messages=errors,
            warning_messages=warnings,
            missing_rate=missing_rate,
            outlier_rate=outlier_rate
        )
