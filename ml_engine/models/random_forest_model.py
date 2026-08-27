"""Balanced Random Forest Classifier with Bootstrap Undersampling.

Constructs an ensemble of de-correlated decision trees, where each tree is trained
on a balanced bootstrap sample created by downsampling the majority class.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from ml_engine.models.base_model import BaseModel


class SimpleDecisionTree:
    """Standard CART classification tree."""

    def __init__(self, max_depth: int = 6, min_samples_split: int = 10, max_features: Optional[int] = None):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.tree_: Optional[Dict[str, Any]] = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "SimpleDecisionTree":
        self.tree_ = self._grow_tree(X, y, depth=0)
        return self

    def _gini(self, y: np.ndarray) -> float:
        if len(y) == 0:
            return 0.0
        p1 = np.sum(y == 1) / len(y)
        return 1.0 - (p1**2 + (1.0 - p1)**2)

    def _grow_tree(self, X: np.ndarray, y: np.ndarray, depth: int) -> Dict[str, Any]:
        n_samples, n_features = X.shape
        n_pos = int(np.sum(y == 1))
        prob = n_pos / max(n_samples, 1)

        if depth >= self.max_depth or n_samples < self.min_samples_split or n_pos == 0 or n_pos == n_samples:
            return {"is_leaf": True, "prob": prob, "samples": n_samples}

        # Subsample features
        n_feats_to_try = self.max_features or int(np.sqrt(n_features)) + 1
        feat_subset = np.random.choice(n_features, size=min(n_feats_to_try, n_features), replace=False)

        best_gini = self._gini(y)
        best_feat = -1
        best_thresh = 0.0

        for f in feat_subset:
            vals = X[:, f]
            quantiles = np.percentile(vals, [25, 50, 75])
            for t in quantiles:
                left = y[vals <= t]
                right = y[vals > t]
                if len(left) == 0 or len(right) == 0:
                    continue

                g_split = (len(left) / n_samples) * self._gini(left) + (len(right) / n_samples) * self._gini(right)
                if g_split < best_gini:
                    best_gini = g_split
                    best_feat = f
                    best_thresh = float(t)

        if best_feat == -1:
            return {"is_leaf": True, "prob": prob, "samples": n_samples}

        mask_l = X[:, best_feat] <= best_thresh
        left_node = self._grow_tree(X[mask_l], y[mask_l], depth + 1)
        right_node = self._grow_tree(X[~mask_l], y[~mask_l], depth + 1)

        return {
            "is_leaf": False,
            "feature": best_feat,
            "threshold": best_thresh,
            "left": left_node,
            "right": right_node,
            "prob": prob,
        }

    def predict_proba_single(self, x: np.ndarray, node: Optional[Dict[str, Any]] = None) -> float:
        curr = node or self.tree_
        if curr is None or curr["is_leaf"]:
            return curr["prob"] if curr else 0.0

        if x[curr["feature"]] <= curr["threshold"]:
            return self.predict_proba_single(x, curr["left"])
        return self.predict_proba_single(x, curr["right"])


class BalancedRandomForestClassifier(BaseModel):
    """Ensemble of Balanced Trees with Majority Downsampling."""

    def __init__(
        self,
        n_estimators: int = 30,
        max_depth: int = 6,
        min_samples_split: int = 8,
        version: str = "1.5.0"
    ):
        super().__init__(model_name="Balanced_Random_Forest", version=version)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.trees: List[SimpleDecisionTree] = []

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None, **kwargs) -> "BalancedRandomForestClassifier":
        if feature_names:
            self.feature_names = feature_names

        minority_idx = np.where(y == 1)[0]
        majority_idx = np.where(y == 0)[0]
        n_min = len(minority_idx)

        self.trees = []
        for _ in range(self.n_estimators):
            # Bootstrap sample minority with replacement
            sampled_min = np.random.choice(minority_idx, size=n_min, replace=True)
            # Randomly downsample majority to match minority count
            sampled_maj = np.random.choice(majority_idx, size=min(n_min, len(majority_idx)), replace=False)

            combined_idx = np.concatenate([sampled_min, sampled_maj])
            np.random.shuffle(combined_idx)

            tree = SimpleDecisionTree(max_depth=self.max_depth, min_samples_split=self.min_samples_split)
            tree.fit(X[combined_idx], y[combined_idx])
            self.trees.append(tree)

        self.is_trained = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        n_samples = len(X)
        if not self.trees:
            default_scores = np.full(n_samples, 0.05, dtype=np.float64)
            return np.column_stack([1.0 - default_scores, default_scores])

        tree_preds = np.zeros((len(self.trees), n_samples), dtype=np.float64)

        for t_idx, tree in enumerate(self.trees):
            for i in range(n_samples):
                tree_preds[t_idx, i] = tree.predict_proba_single(X[i])

        # Average probabilities across forest
        mean_p1 = np.mean(tree_preds, axis=0)
        return np.column_stack([1.0 - mean_p1, mean_p1])

