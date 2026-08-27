"""CatBoost Symmetric Oblivious Decision Tree Classifier.

Implements symmetric oblivious trees where the identical split predicate is evaluated
across all tree nodes at a given depth level. Provides GPU/CPU memory efficiency,
cache locality, and resistance to overfitting on high-cardinality financial features.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from ml_engine.models.base_model import BaseModel


class ObliviousTree:
    """Symmetric oblivious decision tree with depth D producing 2^D leaf values."""

    def __init__(self, depth: int = 4, reg_l2: float = 3.0):
        self.depth = depth
        self.reg_l2 = reg_l2
        self.split_features: List[int] = []
        self.split_thresholds: List[float] = []
        self.leaf_values: np.ndarray = np.zeros(2**depth, dtype=np.float64)

    def fit(self, X: np.ndarray, g: np.ndarray, h: np.ndarray) -> "ObliviousTree":
        n_samples, n_features = X.shape
        self.split_features = []
        self.split_thresholds = []

        # Find best split sequentially for each depth layer
        active_bins = np.zeros(n_samples, dtype=np.int32)

        for d in range(self.depth):
            best_gain = -1e9
            best_feat = -1
            best_thresh = 0.0

            for f in range(n_features):
                vals = X[:, f]
                quantiles = np.percentile(vals, [20, 40, 60, 80])
                for t in quantiles:
                    # Evaluate global split gain across all current partitions
                    left_mask = vals <= t
                    gain = 0.0
                    n_partitions = 1 << d

                    for p in range(n_partitions):
                        p_mask = (active_bins == p)
                        if not np.any(p_mask):
                            continue

                        p_L = p_mask & left_mask
                        p_R = p_mask & (~left_mask)

                        G_L = np.sum(g[p_L])
                        H_L = np.sum(h[p_L])
                        G_R = np.sum(g[p_R])
                        H_R = np.sum(h[p_R])

                        gain += (G_L**2) / (H_L + self.reg_l2) + (G_R**2) / (H_R + self.reg_l2)

                    if gain > best_gain:
                        best_gain = gain
                        best_feat = f
                        best_thresh = float(t)

            self.split_features.append(best_feat)
            self.split_thresholds.append(best_thresh)

            # Update active bin indices for next layer
            is_right = (X[:, best_feat] > best_thresh).astype(np.int32)
            active_bins = (active_bins << 1) | is_right

        # Compute optimal leaf values
        n_leaves = 1 << self.depth
        self.leaf_values = np.zeros(n_leaves, dtype=np.float64)
        for leaf_idx in range(n_leaves):
            mask = (active_bins == leaf_idx)
            if np.any(mask):
                G = np.sum(g[mask])
                H = np.sum(h[mask])
                self.leaf_values[leaf_idx] = -G / (H + self.reg_l2)

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Fast vectorized binary bitwise leaf index lookup."""
        n_samples = len(X)
        leaf_indices = np.zeros(n_samples, dtype=np.int32)
        for d in range(self.depth):
            feat = self.split_features[d]
            thresh = self.split_thresholds[d]
            is_right = (X[:, feat] > thresh).astype(np.int32)
            leaf_indices = (leaf_indices << 1) | is_right

        return self.leaf_values[leaf_indices]


class CatBoostFraudClassifier(BaseModel):
    """CatBoost-style symmetric oblivious tree ensemble for fraud risk scoring."""

    def __init__(
        self,
        n_estimators: int = 30,
        depth: int = 4,
        learning_rate: float = 0.09,
        reg_l2: float = 3.0,
        scale_pos_weight: float = 12.0,
        version: str = "1.2.0"
    ):
        super().__init__(model_name="CatBoost_Fraud_Classifier", version=version)
        self.n_estimators = n_estimators
        self.depth = depth
        self.learning_rate = learning_rate
        self.reg_l2 = reg_l2
        self.scale_pos_weight = scale_pos_weight
        self.trees: List[ObliviousTree] = []
        self.base_score: float = 0.0

    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -15.0, 15.0)))

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None, **kwargs) -> "CatBoostFraudClassifier":
        if feature_names:
            self.feature_names = feature_names

        n_samples = len(y)
        pos_ratio = np.sum(y == 1) / max(n_samples, 1)
        self.base_score = float(np.log(max(pos_ratio, 1e-4) / (1.0 - max(pos_ratio, 1e-4))))

        y_pred_raw = np.full(n_samples, self.base_score, dtype=np.float64)
        self.trees = []

        for _ in range(self.n_estimators):
            p = self._sigmoid(y_pred_raw)
            weights = np.where(y == 1, self.scale_pos_weight, 1.0)
            g = (p - y) * weights
            h = p * (1.0 - p) * weights

            tree = ObliviousTree(depth=self.depth, reg_l2=self.reg_l2)
            tree.fit(X, g, h)
            self.trees.append(tree)

            step = tree.predict(X)
            y_pred_raw += self.learning_rate * step

        self.is_trained = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        n_samples = len(X)
        raw_scores = np.full(n_samples, self.base_score, dtype=np.float64)

        for tree in self.trees:
            raw_scores += self.learning_rate * tree.predict(X)

        probs = self._sigmoid(raw_scores)
        return np.column_stack([1.0 - probs, probs])
