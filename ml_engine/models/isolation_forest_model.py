"""Isolation Forest Unsupervised Anomaly Detection for Outlier Isolation.

Recursively isolates observation points using random hyperplane partitions.
Anomalous fraud events require significantly fewer recursive splits to isolate.
"""

from __future__ import annotations
import math
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from ml_engine.models.base_model import BaseModel


class IsolationTreeNode:
    """Node in an isolation tree."""
    __slots__ = ("feature_idx", "split_value", "left", "right", "size", "is_leaf")

    def __init__(
        self,
        feature_idx: int = -1,
        split_value: float = 0.0,
        left: Optional["IsolationTreeNode"] = None,
        right: Optional["IsolationTreeNode"] = None,
        size: int = 0,
        is_leaf: bool = False
    ):
        self.feature_idx = feature_idx
        self.split_value = split_value
        self.left = left
        self.right = right
        self.size = size
        self.is_leaf = is_leaf


class IsolationTree:
    """Individual isolation tree."""

    def __init__(self, max_height: int):
        self.max_height = max_height
        self.root: Optional[IsolationTreeNode] = None

    def fit(self, X: np.ndarray, current_height: int = 0) -> IsolationTreeNode:
        n_samples, n_features = X.shape

        if current_height >= self.max_height or n_samples <= 1:
            return IsolationTreeNode(size=n_samples, is_leaf=True)

        # Randomly select a feature and split point between min and max
        feat_idx = np.random.randint(0, n_features)
        feat_min = float(np.min(X[:, feat_idx]))
        feat_max = float(np.max(X[:, feat_idx]))

        if feat_min == feat_max:
            return IsolationTreeNode(size=n_samples, is_leaf=True)

        split_val = float(np.random.uniform(feat_min, feat_max))
        left_mask = X[:, feat_idx] < split_val

        left_node = self.fit(X[left_mask], current_height + 1)
        right_node = self.fit(X[~left_mask], current_height + 1)

        return IsolationTreeNode(
            feature_idx=feat_idx,
            split_value=split_val,
            left=left_node,
            right=right_node,
            size=n_samples,
            is_leaf=False
        )

    def path_length(self, x: np.ndarray, node: IsolationTreeNode, current_depth: int = 0) -> float:
        if node.is_leaf:
            return current_depth + self._c(node.size)

        if x[node.feature_idx] < node.split_value:
            return self.path_length(x, node.left, current_depth + 1)
        return self.path_length(x, node.right, current_depth + 1)

    @staticmethod
    def _c(n: int) -> float:
        """Average path length of unsuccessful search in Binary Search Tree."""
        if n <= 1:
            return 0.0
        if n == 2:
            return 1.0
        euler_mascheroni = 0.5772156649
        return 2.0 * (math.log(n - 1) + euler_mascheroni) - (2.0 * (n - 1) / n)


class IsolationForestAnomalyDetector(BaseModel):
    """Ensemble of Isolation Trees calculating anomaly score $s(x, n) = 2^{-E(h(x)) / c(n)}$."""

    def __init__(
        self,
        n_estimators: int = 50,
        max_samples: int = 256,
        contamination: float = 0.03,
        version: str = "1.3.0"
    ):
        super().__init__(model_name="Isolation_Forest_Detector", version=version)
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.contamination = contamination
        self.trees: List[IsolationTree] = []
        self.max_height = int(math.ceil(math.log2(max(max_samples, 2))))
        self.c_subsample = IsolationTree._c(max_samples)

    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None, feature_names: Optional[List[str]] = None, **kwargs) -> "IsolationForestAnomalyDetector":
        if feature_names:
            self.feature_names = feature_names

        n_samples = len(X)
        subsample_size = min(self.max_samples, n_samples)
        self.c_subsample = IsolationTree._c(subsample_size)
        self.trees = []

        for _ in range(self.n_estimators):
            sample_idx = np.random.choice(n_samples, size=subsample_size, replace=False)
            tree = IsolationTree(max_height=self.max_height)
            tree.root = tree.fit(X[sample_idx])
            self.trees.append(tree)

        self.is_trained = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        n_samples = len(X)
        avg_path_lengths = np.zeros(n_samples, dtype=np.float64)

        for tree in self.trees:
            for i in range(n_samples):
                avg_path_lengths[i] += tree.path_length(X[i], tree.root)

        avg_path_lengths /= len(self.trees)

        # Anomaly score formula
        scores = 2.0 ** (-avg_path_lengths / max(self.c_subsample, 1e-6))
        return np.column_stack([1.0 - scores, scores])
