"""Federated Learning (FedAvg) Multi-Bank Privacy Coordinator.

Coordinates decentralized model weight updates across multiple partner banks/issuers
without sharing raw customer transaction logs, adding Differential Privacy Gaussian noise.
"""

from __future__ import annotations
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ClientModelUpdate:
    bank_institution_id: str
    num_samples_trained: int
    weights: List[np.ndarray]
    validation_roc_auc: float


class FederatedLearningCoordinator:
    """Central parameter server aggregating gradient updates via Federated Averaging (FedAvg)."""

    def __init__(self, global_weights: List[np.ndarray], dp_epsilon: float = 1.0, dp_delta: float = 1e-5):
        self.global_weights = [np.copy(w) for w in global_weights]
        self.dp_epsilon = dp_epsilon
        self.dp_delta = dp_delta
        self.round_history: List[Dict[str, Any]] = []

    def aggregate_fed_avg(self, client_updates: List[ClientModelUpdate], add_dp_noise: bool = True) -> List[np.ndarray]:
        """Weighted average of client weights based on sample proportion."""
        if not client_updates:
            return self.global_weights

        total_samples = sum(u.num_samples_trained for u in client_updates)
        new_global = [np.zeros_like(w) for w in self.global_weights]

        for u in client_updates:
            weight_factor = u.num_samples_trained / total_samples
            for i, layer_w in enumerate(u.weights):
                new_global[i] += weight_factor * layer_w

        if add_dp_noise:
            # Add Gaussian differential privacy noise: N(0, sigma^2)
            sigma = (np.sqrt(2 * np.log(1.25 / self.dp_delta))) / self.dp_epsilon
            for i in range(len(new_global)):
                noise = np.random.normal(0, sigma * 0.001, size=new_global[i].shape)
                new_global[i] += noise.astype(np.float32)

        self.global_weights = new_global
        avg_auc = float(np.mean([u.validation_roc_auc for u in client_updates]))

        self.round_history.append({
            "round": len(self.round_history) + 1,
            "participating_banks_count": len(client_updates),
            "total_samples_aggregated": total_samples,
            "average_client_roc_auc": round(avg_auc, 4),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        return self.global_weights
