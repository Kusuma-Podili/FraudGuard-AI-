"""Class Imbalance and Resampling Strategies for Extreme Fraud Disproportions.

Credit card fraud typically manifests at severe imbalance ratios (0.1% - 0.5% positive fraud rate).
This module implements resampling strategies and cost-sensitive reweighting:
- Synthetic Minority Over-sampling Technique (SMOTE)
- Adaptive Synthetic Sampling (ADASYN)
- Borderline-SMOTE
- Tomek Links majority cleaning
- Balanced Class Weight calculation (King & Zeng, 2001)
- Effective Number of Samples weighting (Cui et al., CVPR 2019)
"""

from __future__ import annotations
import math
import random
from typing import Tuple, Optional, List, Dict
import numpy as np


class ClassWeightCalculator:
    """Calculates optimal cost-sensitive loss weights for imbalanced binary classification."""

    @staticmethod
    def compute_balanced_weights(y: np.ndarray) -> Dict[int, float]:
        """Standard inverse frequency weights: n_samples / (n_classes * count_k)."""
        n_samples = len(y)
        classes, counts = np.unique(y, return_counts=True)
        n_classes = len(classes)
        weights = {}
        for cls, count in zip(classes, counts):
            weights[int(cls)] = float(n_samples / (n_classes * count))
        return weights

    @staticmethod
    def compute_effective_num_weights(y: np.ndarray, beta: float = 0.9999) -> Dict[int, float]:
        """Class-Balanced Loss Based on Effective Number of Samples (Cui et al. 2019).

        Weight = (1 - beta) / (1 - beta^N_y)
        """
        classes, counts = np.unique(y, return_counts=True)
        weights = {}
        for cls, n_y in zip(classes, counts):
            effective_num = 1.0 - (beta ** n_y)
            weights[int(cls)] = float((1.0 - beta) / max(effective_num, 1e-8))

        # Normalize weights so sum equals n_classes
        total = sum(weights.values())
        for cls in weights:
            weights[cls] = (weights[cls] / total) * len(classes)
        return weights


class BalanceHandler:
    """Base interface for resampling techniques."""

    def fit_resample(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        raise NotImplementedError


class SMOTEHandler(BalanceHandler):
    """Synthetic Minority Over-sampling Technique (Chawla et al., 2002).

    Synthesizes new instances along the feature segments joining k-nearest minority neighbors.
    """

    def __init__(self, sampling_ratio: float = 0.25, k_neighbors: int = 5, random_state: Optional[int] = 42):
        self.sampling_ratio = sampling_ratio
        self.k_neighbors = k_neighbors
        self.random_state = random_state

    def _euclidean_distances(self, x: np.ndarray, Y: np.ndarray) -> np.ndarray:
        return np.sqrt(np.sum((Y - x) ** 2, axis=1))

    def fit_resample(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        rng = np.random.default_rng(self.random_state)
        minority_mask = (y == 1)
        majority_mask = (y == 0)

        X_min = X[minority_mask]
        X_maj = X[majority_mask]
        n_min = len(X_min)
        n_maj = len(X_maj)

        if n_min < 2:
            return X, y

        target_n_min = int(n_maj * self.sampling_ratio)
        n_synthetic_needed = max(0, target_n_min - n_min)

        if n_synthetic_needed == 0:
            return X, y

        synthetic_samples = []
        k = min(self.k_neighbors, n_min - 1)

        # Precompute k-nearest neighbors for minority samples
        for _ in range(n_synthetic_needed):
            idx = rng.integers(0, n_min)
            sample = X_min[idx]

            # Find distances to other minority samples
            distances = self._euclidean_distances(sample, X_min)
            neighbor_indices = np.argsort(distances)[1 : k + 1]

            chosen_neighbor_idx = rng.choice(neighbor_indices)
            neighbor = X_min[chosen_neighbor_idx]

            # Interpolation: x_new = x + lambda * (neighbor - x)
            gap = neighbor - sample
            lam = rng.uniform(0.0, 1.0)
            synth = sample + lam * gap
            synthetic_samples.append(synth)

        X_synth = np.array(synthetic_samples, dtype=X.dtype)
        y_synth = np.ones(len(synthetic_samples), dtype=y.dtype)

        X_resampled = np.vstack([X, X_synth])
        y_resampled = np.concatenate([y, y_synth])

        return X_resampled, y_resampled


class ADASYNHandler(BalanceHandler):
    """Adaptive Synthetic (ADASYN) sampling approach for imbalanced learning (He et al., 2008).

    Samples difficult minority instances (those surrounded by majority class) with higher density.
    """

    def __init__(self, sampling_ratio: float = 0.25, k_neighbors: int = 5, random_state: Optional[int] = 42):
        self.sampling_ratio = sampling_ratio
        self.k_neighbors = k_neighbors
        self.random_state = random_state

    def fit_resample(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        rng = np.random.default_rng(self.random_state)
        minority_mask = (y == 1)
        X_min = X[minority_mask]
        n_min = len(X_min)
        n_maj = int(np.sum(y == 0))

        if n_min < 2:
            return X, y

        total_synthetic_needed = max(0, int((n_maj - n_min) * self.sampling_ratio))
        if total_synthetic_needed == 0:
            return X, y

        k = min(self.k_neighbors, len(X) - 1)
        ratios = []

        # Step 1: Calculate difficulty ratio r_i for each minority sample
        for i in range(n_min):
            sample = X_min[i]
            dists = np.sqrt(np.sum((X - sample) ** 2, axis=1))
            k_indices = np.argsort(dists)[1 : k + 1]
            # Ratio of majority neighbors
            majority_count = np.sum(y[k_indices] == 0)
            ratios.append(majority_count / k)

        ratios = np.array(ratios, dtype=np.float64)
        sum_ratios = np.sum(ratios)

        if sum_ratios == 0:
            # Fall back to uniform distribution
            density = np.ones(n_min) / n_min
        else:
            density = ratios / sum_ratios

        # Step 2: Synthesize samples proportional to difficulty density
        synthetic_samples = []
        samples_per_point = np.round(density * total_synthetic_needed).astype(int)

        for i, count in enumerate(samples_per_point):
            if count == 0:
                continue
            sample = X_min[i]
            min_dists = np.sqrt(np.sum((X_min - sample) ** 2, axis=1))
            k_min = min(self.k_neighbors, n_min - 1)
            min_neighbors = np.argsort(min_dists)[1 : k_min + 1]

            for _ in range(count):
                neighbor = X_min[rng.choice(min_neighbors)]
                synth = sample + rng.uniform(0.0, 1.0) * (neighbor - sample)
                synthetic_samples.append(synth)

        if not synthetic_samples:
            return X, y

        X_synth = np.array(synthetic_samples, dtype=X.dtype)
        y_synth = np.ones(len(synthetic_samples), dtype=y.dtype)

        return np.vstack([X, X_synth]), np.concatenate([y, y_synth])
