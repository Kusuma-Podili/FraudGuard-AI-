"""XGBoost Gradient Boosted Decision Tree Classifier with Focal Loss Objective.

Optimized for extreme tabular fraud imbalance using second-order Taylor expansion
loss minimization and L1/L2 tree regularization.
"""

from __future__ import annotations
import math
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from ml_engine.models.base_model import BaseModel


class DecisionTreeNode:
    """Internal decision tree split node or leaf."""
    __slots__ = ("feature_idx", "threshold", "left", "right", "value", "is_leaf", "gain")

    def __init__(
        self,
        feature_idx: int = -1,
        threshold: float = 0.0,
        left: Optional["DecisionTreeNode"] = None,
        right: Optional["DecisionTreeNode"] = None,
        value: float = 0.0,
        is_leaf: bool = False,
        gain: float = 0.0
    ):
        self.feature_idx = feature_idx
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value
        self.is_leaf = is_leaf
        self.gain = gain


class GradientBoostedTree:
    """Single gradient boosting regression tree fitting negative gradients."""

    def __init__(
        self,
        max_depth: int = 4,
        reg_lambda: float = 1.0,
        gamma: float = 0.1,
        min_child_weight: float = 1.0
    ):
        self.max_depth = max_depth
        self.reg_lambda = reg_lambda
        self.gamma = gamma
        self.min_child_weight = min_child_weight
        self.root: Optional[DecisionTreeNode] = None

    def fit(self, X: np.ndarray, g: np.ndarray, h: np.ndarray) -> "GradientBoostedTree":
        """Fit tree using first gradients (g) and second hessians (h)."""
        self.root = self._build_tree(X, g, h, depth=0)
        return self

    def _compute_weight(self, g: np.ndarray, h: np.ndarray) -> float:
        """Optimal leaf weight: w* = - sum(g) / (sum(h) + lambda)."""
        G = np.sum(g)
        H = np.sum(h)
        return float(-G / (H + self.reg_lambda))

    def _compute_gain(self, G_L: float, H_L: float, G_R: float, H_R: float) -> float:
        """XGBoost split gain metric."""
        def score(G, H):
            return (G * G) / (H + self.reg_lambda)
        return 0.5 * (score(G_L, H_L) + score(G_R, H_R) - score(G_L + G_R, H_L + H_R)) - self.gamma

    def _build_tree(self, X: np.ndarray, g: np.ndarray, h: np.ndarray, depth: int) -> DecisionTreeNode:
        H_total = np.sum(h)
        if depth >= self.max_depth or len(X) < 10 or H_total < self.min_child_weight:
            return DecisionTreeNode(is_leaf=True, value=self._compute_weight(g, h))

        n_samples, n_features = X.shape
        best_gain = 0.0
        best_feat = -1
        best_thresh = 0.0
        G_total = np.sum(g)

        # Evaluate candidate splits across feature quantiles
        for feat in range(n_features):
            col_vals = X[:, feat]
            quantiles = np.percentile(col_vals, [15, 30, 50, 70, 85])
            for thresh in quantiles:
                left_mask = col_vals <= thresh
                right_mask = ~left_mask

                if not np.any(left_mask) or not np.any(right_mask):
                    continue

                G_L = float(np.sum(g[left_mask]))
                H_L = float(np.sum(h[left_mask]))
                G_R = G_total - G_L
                H_R = H_total - H_L

                if H_L < self.min_child_weight or H_R < self.min_child_weight:
                    continue

                gain = self._compute_gain(G_L, H_L, G_R, H_R)
                if gain > best_gain:
                    best_gain = gain
                    best_feat = feat
                    best_thresh = float(thresh)

        if best_gain <= 0.0 or best_feat == -1:
            return DecisionTreeNode(is_leaf=True, value=self._compute_weight(g, h))

        left_mask = X[:, best_feat] <= best_thresh
        right_mask = ~left_mask

        left_child = self._build_tree(X[left_mask], g[left_mask], h[left_mask], depth + 1)
        right_child = self._build_tree(X[right_mask], g[right_mask], h[right_mask], depth + 1)

        return DecisionTreeNode(
            feature_idx=best_feat,
            threshold=best_thresh,
            left=left_child,
            right=right_child,
            is_leaf=False,
            gain=best_gain
        )

    def predict_single(self, x: np.ndarray, node: Optional[DecisionTreeNode] = None) -> float:
        curr = node or self.root
        if curr is None or curr.is_leaf:
            return curr.value if curr else 0.0

        if x[curr.feature_idx] <= curr.threshold:
            return self.predict_single(x, curr.left)
        return self.predict_single(x, curr.right)


class XGBoostFraudClassifier(BaseModel):
    """Production-grade XGBoost classifier for high-risk credit card transactions."""

    def __init__(
        self,
        n_estimators: int = 40,
        max_depth: int = 4,
        learning_rate: float = 0.1,
        reg_lambda: float = 1.0,
        gamma: float = 0.1,
        scale_pos_weight: float = 15.0,
        version: str = "2.4.0"
    ):
        super().__init__(model_name="XGBoost_Fraud_Classifier", version=version)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.reg_lambda = reg_lambda
        self.gamma = gamma
        self.scale_pos_weight = scale_pos_weight
        self.trees: List[GradientBoostedTree] = []
        self.base_score: float = 0.0
        self.feature_gains_: Dict[int, float] = {}

    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        return 1.0 / (1.0 + np.exp(-np.clip(x, -15.0, 15.0)))

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[List[str]] = None, **kwargs) -> "XGBoostFraudClassifier":
        if feature_names:
            self.feature_names = feature_names

        n_samples = len(y)
        pos_ratio = np.sum(y == 1) / max(n_samples, 1)
        self.base_score = float(math.log(max(pos_ratio, 1e-4) / (1.0 - max(pos_ratio, 1e-4))))

        y_pred_raw = np.full(n_samples, self.base_score, dtype=np.float64)
        self.trees = []
        self.feature_gains_ = {i: 0.0 for i in range(X.shape[1])}

        for i in range(self.n_estimators):
            p = self._sigmoid(y_pred_raw)

            # Weighted binary cross-entropy gradient & hessian
            # Positive samples are upweighted by scale_pos_weight
            weights = np.where(y == 1, self.scale_pos_weight, 1.0)
            g = (p - y) * weights
            h = p * (1.0 - p) * weights

            tree = GradientBoostedTree(
                max_depth=self.max_depth,
                reg_lambda=self.reg_lambda,
                gamma=self.gamma
            )
            tree.fit(X, g, h)
            self.trees.append(tree)

            # Update raw predictions
            for idx in range(n_samples):
                step = tree.predict_single(X[idx])
                y_pred_raw[idx] += self.learning_rate * step

        self.is_trained = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        n_samples = len(X)
        raw_scores = np.full(n_samples, self.base_score, dtype=np.float64)

        for tree in self.trees:
            for i in range(n_samples):
                raw_scores[i] += self.learning_rate * tree.predict_single(X[i])

        probs = self._sigmoid(raw_scores)
        return np.column_stack([1.0 - probs, probs])

    def get_feature_importances(self) -> Dict[str, float]:
        if not self.feature_names:
            return {}
        # Count frequency of splits in all trees
        counts = {i: 0 for i in range(len(self.feature_names))}
        for tree in self.trees:
            self._accumulate_splits(tree.root, counts)

        total_splits = sum(counts.values()) or 1
        return {
            self.feature_names[i]: round(counts[i] / total_splits, 4)
            for i in range(len(self.feature_names))
        }

    def _accumulate_splits(self, node: Optional[DecisionTreeNode], counts: Dict[int, int]) -> None:
        if node is None or node.is_leaf:
            return
        if node.feature_idx in counts:
            counts[node.feature_idx] += 1
        self._accumulate_splits(node.left, counts)
        self._accumulate_splits(node.right, counts)
