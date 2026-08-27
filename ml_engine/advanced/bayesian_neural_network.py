"""Bayesian Neural Network & Monte Carlo Dropout for Epistemic Uncertainty.

Quantifies epistemic (model ignorance) vs aleatoric (data noise) uncertainty
on borderline transaction authorizations to avoid high-confidence false rejections.
"""

from __future__ import annotations
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class UncertaintyScoreResult:
    mean_fraud_probability: float
    epistemic_uncertainty_std: float  # Variance across MC passes
    confidence_interval_low: float
    confidence_interval_high: float
    is_high_uncertainty: bool
    requires_human_escalation: bool


class BayesianMonteCarloClassifier:
    """Bayesian approximation using test-time Monte Carlo Dropout sampling."""

    def __init__(self, input_dim: int = 16, hidden_dim: int = 32, dropout_rate: float = 0.25, seed: int = 42):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.dropout_rate = dropout_rate

        rng = np.random.RandomState(seed)
        self.w1 = rng.randn(input_dim, hidden_dim).astype(np.float32) * np.sqrt(2.0 / input_dim)
        self.b1 = np.zeros(hidden_dim, dtype=np.float32)
        self.w2 = rng.randn(hidden_dim, 1).astype(np.float32) * np.sqrt(2.0 / hidden_dim)
        self.b2 = np.zeros(1, dtype=np.float32)

    def _single_forward_pass(self, x: np.ndarray, apply_dropout: bool = True) -> float:
        # Layer 1 + ReLU
        h = np.maximum(0.0, np.dot(x, self.w1) + self.b1)

        if apply_dropout:
            mask = (np.random.rand(*h.shape) > self.dropout_rate).astype(np.float32)
            h = (h * mask) / (1.0 - self.dropout_rate)

        # Layer 2 + Sigmoid
        logit = np.dot(h, self.w2) + self.b2
        prob = 1.0 / (1.0 + np.exp(-logit[0]))
        return float(prob)

    def predict_with_uncertainty(self, x: np.ndarray, num_mc_samples: int = 30) -> UncertaintyScoreResult:
        """Execute Monte Carlo stochastic forward passes to compute posterior distribution."""
        samples = [self._single_forward_pass(x, apply_dropout=True) for _ in range(num_mc_samples)]
        mean_p = float(np.mean(samples))
        std_p = float(np.std(samples))

        ci_low = max(0.0, mean_p - 1.96 * std_p)
        ci_high = min(1.0, mean_p + 1.96 * std_p)

        is_uncertain = std_p > 0.12
        needs_human = bool(is_uncertain and 0.35 <= mean_p <= 0.75)

        return UncertaintyScoreResult(
            mean_fraud_probability=round(mean_p, 4),
            epistemic_uncertainty_std=round(std_p, 4),
            confidence_interval_low=round(ci_low, 4),
            confidence_interval_high=round(ci_high, 4),
            is_high_uncertainty=is_uncertain,
            requires_human_escalation=needs_human,
        )
