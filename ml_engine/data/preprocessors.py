"""Advanced Tabular Data Preprocessing and Feature Encoding for Credit Card Fraud Detection.

Provides robust mathematical transformations:
- Cyclical trigonometric temporal embeddings (sin/cos of hour, day of week, day of month)
- Robust outlier-resistant scaling (median/IQR scaling)
- Weight of Evidence (WoE) and Information Value (IV) encoding
- Smoothed Empirical Bayes Target Encoding
- Automated categorical and numeric pipeline orchestration
"""

from __future__ import annotations
import math
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np


class CyclicalTimeEncoder:
    """Encodes cyclical temporal features into 2D continuous sine and cosine components.

    Preserves distance continuity across boundaries (e.g. 23:59 -> 00:00).
    """

    def __init__(self, cycle_periods: Optional[Dict[str, float]] = None):
        """Initialize with mapping of feature name to cycle period.

        Default periods:
        - hour_of_day: 24.0
        - day_of_week: 7.0
        - day_of_month: 31.0
        - month_of_year: 12.0
        """
        self.cycle_periods = cycle_periods or {
            "hour_of_day": 24.0,
            "day_of_week": 7.0,
            "day_of_month": 31.0,
            "month_of_year": 12.0,
        }

    def transform_value(self, value: float, period: float) -> Tuple[float, float]:
        """Convert a single scalar value into (sin, cos) coordinates."""
        radians = 2.0 * math.pi * (value / period)
        return math.sin(radians), math.cos(radians)

    def transform_dict(self, record: Dict[str, Any]) -> Dict[str, float]:
        """Add cyclical sin/cos features to an input record dictionary."""
        transformed = {}
        for feature_name, period in self.cycle_periods.items():
            if feature_name in record and record[feature_name] is not None:
                val = float(record[feature_name])
                sin_val, cos_val = self.transform_value(val, period)
                transformed[f"{feature_name}_sin"] = round(sin_val, 6)
                transformed[f"{feature_name}_cos"] = round(cos_val, 6)
        return transformed


class RobustOutlierScaler:
    """Scales features using statistics that are robust to extreme outliers.

    Uses the median and the Interquartile Range (IQR):
    x_scaled = (x - median) / (Q75 - Q25)
    """

    def __init__(self, quantile_range: Tuple[float, float] = (25.0, 75.0), unit_variance: bool = False):
        self.quantile_range = quantile_range
        self.unit_variance = unit_variance
        self.center_: Dict[str, float] = {}
        self.scale_: Dict[str, float] = {}
        self.is_fitted: bool = False

    def fit(self, data: Dict[str, List[float]]) -> "RobustOutlierScaler":
        """Compute the median and IQR for each numerical feature."""
        q_min, q_max = self.quantile_range
        for feature, values in data.items():
            arr = np.array(values, dtype=np.float64)
            arr = arr[~np.isnan(arr)]
            if len(arr) == 0:
                self.center_[feature] = 0.0
                self.scale_[feature] = 1.0
                continue

            med = float(np.median(arr))
            q25 = float(np.percentile(arr, q_min))
            q75 = float(np.percentile(arr, q_max))
            iqr = q75 - q25

            if iqr == 0.0:
                iqr = float(np.std(arr)) if np.std(arr) > 1e-6 else 1.0

            self.center_[feature] = med
            self.scale_[feature] = iqr

        self.is_fitted = True
        return self

    def transform_value(self, feature: str, value: float) -> float:
        """Transform a single feature value."""
        if not self.is_fitted or feature not in self.center_:
            return value
        med = self.center_[feature]
        scale = self.scale_[feature]
        return (value - med) / scale if scale > 0 else 0.0

    def transform_dict(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Transform all known numeric features in a dictionary."""
        result = dict(record)
        for feature, val in record.items():
            if feature in self.center_ and isinstance(val, (int, float)):
                result[f"{feature}_robust_scaled"] = round(self.transform_value(feature, float(val)), 6)
        return result


class WeightOfEvidenceEncoder:
    """Weight of Evidence (WoE) and Information Value (IV) categorical encoder.

    WoE = ln( % Good / % Bad ) = ln( (Good_i / Total_Good) / (Bad_i / Total_Bad) )
    IV = sum( (% Good - % Bad) * WoE )
    """

    def __init__(self, smoothing: float = 0.5):
        self.smoothing = smoothing
        self.woe_maps_: Dict[str, Dict[str, float]] = {}
        self.iv_scores_: Dict[str, float] = {}
        self.default_woe_: Dict[str, float] = {}

    def fit(self, categories: Dict[str, List[str]], labels: List[int]) -> "WeightOfEvidenceEncoder":
        y = np.array(labels, dtype=np.int32)
        total_bad = int(np.sum(y == 1))
        total_good = int(np.sum(y == 0))

        if total_bad == 0 or total_good == 0:
            return self

        for feature_name, cat_list in categories.items():
            unique_cats = set(cat_list)
            self.woe_maps_[feature_name] = {}
            iv_total = 0.0

            for cat in unique_cats:
                mask = np.array([c == cat for c in cat_list], dtype=bool)
                cat_bad = int(np.sum(y[mask] == 1)) + self.smoothing
                cat_good = int(np.sum(y[mask] == 0)) + self.smoothing

                pct_bad = cat_bad / (total_bad + 2 * self.smoothing)
                pct_good = cat_good / (total_good + 2 * self.smoothing)

                woe = math.log(pct_good / pct_bad)
                self.woe_maps_[feature_name][cat] = round(woe, 5)
                iv_total += (pct_good - pct_bad) * woe

            self.iv_scores_[feature_name] = round(iv_total, 5)
            self.default_woe_[feature_name] = 0.0

        return self

    def transform_value(self, feature: str, category: str) -> float:
        if feature in self.woe_maps_ and category in self.woe_maps_[feature]:
            return self.woe_maps_[feature][category]
        return self.default_woe_.get(feature, 0.0)


class TargetEncoder:
    """Smoothed empirical Bayes target encoder for high-cardinality categoricals (e.g. Merchant ID, Zip).

    Formula:
    S_i = (n_i * y_bar_i + m * global_mean) / (n_i + m)
    where m is the smoothing weight parameter.
    """

    def __init__(self, smoothing: float = 10.0):
        self.smoothing = smoothing
        self.encodings_: Dict[str, Dict[str, float]] = {}
        self.global_mean_: Dict[str, float] = {}

    def fit(self, categories: Dict[str, List[str]], labels: List[int]) -> "TargetEncoder":
        y = np.array(labels, dtype=np.float64)
        global_mean = float(np.mean(y)) if len(y) > 0 else 0.0

        for feature_name, cat_list in categories.items():
            self.global_mean_[feature_name] = global_mean
            self.encodings_[feature_name] = {}

            unique_cats = set(cat_list)
            for cat in unique_cats:
                cat_indices = [i for i, c in enumerate(cat_list) if c == cat]
                n_i = len(cat_indices)
                y_bar_i = float(np.mean(y[cat_indices])) if n_i > 0 else global_mean

                # Empirical Bayes smoothing
                smoothed = (n_i * y_bar_i + self.smoothing * global_mean) / (n_i + self.smoothing)
                self.encodings_[feature_name][cat] = round(smoothed, 6)

        return self

    def transform_value(self, feature: str, category: str) -> float:
        if feature in self.encodings_ and category in self.encodings_[feature]:
            return self.encodings_[feature][category]
        return self.global_mean_.get(feature, 0.0)


class TabularPreprocessor:
    """Unified tabular preprocessor executing the complete transformation pipeline."""

    def __init__(
        self,
        numeric_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
        temporal_features: Optional[List[str]] = None,
    ):
        self.numeric_features = numeric_features or [
            "amount", "cardholder_age", "distance_from_home_km", "velocity_1h",
            "velocity_24h", "amount_ratio_to_mean_30d", "failed_pin_attempts_24h"
        ]
        self.categorical_features = categorical_features or [
            "merchant_category", "entry_mode", "card_type", "card_network",
            "device_type", "transaction_channel", "country_code"
        ]
        self.temporal_features = temporal_features or [
            "hour_of_day", "day_of_week"
        ]

        self.cyclical_encoder = CyclicalTimeEncoder()
        self.robust_scaler = RobustOutlierScaler()
        self.target_encoder = TargetEncoder(smoothing=15.0)
        self.woe_encoder = WeightOfEvidenceEncoder()
        self.feature_names_out_: List[str] = []

    def fit(self, dataset: List[Dict[str, Any]], labels: Optional[List[int]] = None) -> "TabularPreprocessor":
        """Fit all transformers on the training dataset."""
        # Extract numeric columns
        numeric_data = {feat: [float(d.get(feat, 0.0) or 0.0) for d in dataset] for feat in self.numeric_features}
        self.robust_scaler.fit(numeric_data)

        if labels is not None and len(labels) == len(dataset):
            cat_data = {feat: [str(d.get(feat, "UNKNOWN")) for d in dataset] for feat in self.categorical_features}
            self.target_encoder.fit(cat_data, labels)
            self.woe_encoder.fit(cat_data, labels)

        # Build output feature schema
        out_names = []
        for feat in self.numeric_features:
            out_names.append(f"{feat}_norm")
        for feat in self.temporal_features:
            out_names.append(f"{feat}_sin")
            out_names.append(f"{feat}_cos")
        for feat in self.categorical_features:
            out_names.append(f"{feat}_target_encoded")
            out_names.append(f"{feat}_woe")

        self.feature_names_out_ = out_names
        return self

    def transform_single(self, record: Dict[str, Any]) -> np.ndarray:
        """Transform a single transaction record into a 1D float numpy feature vector."""
        vec = []

        # 1. Numeric features
        for feat in self.numeric_features:
            val = float(record.get(feat, 0.0) or 0.0)
            norm_val = self.robust_scaler.transform_value(feat, val)
            vec.append(norm_val)

        # 2. Temporal cyclical features
        cyclical = self.cyclical_encoder.transform_dict(record)
        for feat in self.temporal_features:
            vec.append(cyclical.get(f"{feat}_sin", 0.0))
            vec.append(cyclical.get(f"{feat}_cos", 0.0))

        # 3. Categorical encodings
        for feat in self.categorical_features:
            cat_val = str(record.get(feat, "UNKNOWN"))
            te_val = self.target_encoder.transform_value(feat, cat_val)
            woe_val = self.woe_encoder.transform_value(feat, cat_val)
            vec.append(te_val)
            vec.append(woe_val)

        return np.array(vec, dtype=np.float32)

    def transform_batch(self, records: List[Dict[str, Any]]) -> np.ndarray:
        """Transform a batch of records into a 2D matrix (N, num_features)."""
        matrix = [self.transform_single(r) for r in records]
        return np.vstack(matrix)
