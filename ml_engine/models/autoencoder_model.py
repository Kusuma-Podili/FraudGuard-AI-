"""Deep Autoencoder Neural Network for Unsupervised Anomaly Detection.

Trained exclusively on legitimate transaction patterns. Anomalous fraud behaviors
exhibit high Mean Squared Reconstruction Error (MSE) when mapped through the bottleneck latent manifold.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from ml_engine.models.base_model import BaseModel


class DeepAutoencoderAnomalyDetector(BaseModel):
    """Deep Symmetrical Autoencoder (Input -> 32 -> 16 -> 8 -> 16 -> 32 -> Output)."""

    def __init__(
        self,
        hidden_dims: Tuple[int, int, int] = (16, 8, 4),
        learning_rate: float = 0.01,
        epochs: int = 40,
        batch_size: int = 64,
        contamination: float = 0.03,
        version: str = "2.0.1"
    ):
        super().__init__(model_name="Deep_Autoencoder_Anomaly_Detector", version=version)
        self.hidden_dims = hidden_dims
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.contamination = contamination
        self.weights: List[np.ndarray] = []
        self.biases: List[np.ndarray] = []
        self.reconstruction_threshold: float = 1.0

    def _relu(self, z: np.ndarray) -> np.ndarray:
        return np.maximum(0.0, z)

    def _relu_deriv(self, a: np.ndarray) -> np.ndarray:
        return (a > 0.0).astype(np.float64)

    def _init_weights(self, input_dim: int) -> None:
        """He (Kaiming) normal weight initialization."""
        h1, h2, bottleneck = self.hidden_dims
        layer_dims = [input_dim, h1, h2, bottleneck, h2, h1, input_dim]

        self.weights = []
        self.biases = []
        rng = np.random.default_rng(42)

        for i in range(len(layer_dims) - 1):
            fan_in = layer_dims[i]
            fan_out = layer_dims[i + 1]
            limit = np.sqrt(2.0 / fan_in)
            W = rng.normal(0.0, limit, size=(fan_in, fan_out)).astype(np.float64)
            b = np.zeros(fan_out, dtype=np.float64)
            self.weights.append(W)
            self.biases.append(b)

    def _forward(self, X: np.ndarray) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """Compute forward pass caching pre-activations (Z) and activations (A)."""
        activations = [X]
        z_list = []
        curr = X

        # Hidden layers with LeakyReLU/ReLU
        for layer_idx in range(len(self.weights) - 1):
            Z = np.dot(curr, self.weights[layer_idx]) + self.biases[layer_idx]
            A = self._relu(Z)
            z_list.append(Z)
            activations.append(A)
            curr = A

        # Output reconstruction layer (linear activation)
        last_idx = len(self.weights) - 1
        Z_out = np.dot(curr, self.weights[last_idx]) + self.biases[last_idx]
        z_list.append(Z_out)
        activations.append(Z_out)

        return activations, z_list

    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None, feature_names: Optional[List[str]] = None, **kwargs) -> "DeepAutoencoderAnomalyDetector":
        if feature_names:
            self.feature_names = feature_names

        # Train exclusively on normal / legitimate transactions (y == 0) if labels provided
        if y is not None:
            X_train = X[y == 0]
        else:
            X_train = X

        n_samples, input_dim = X_train.shape
        self._init_weights(input_dim)

        # Mini-batch Gradient Descent with Momentum
        v_W = [np.zeros_like(w) for w in self.weights]
        v_b = [np.zeros_like(b) for b in self.biases]
        momentum = 0.9

        for epoch in range(self.epochs):
            perm = np.random.permutation(n_samples)
            X_shuffled = X_train[perm]

            for b_start in range(0, n_samples, self.batch_size):
                b_end = min(b_start + self.batch_size, n_samples)
                X_batch = X_shuffled[b_start:b_end]
                m = len(X_batch)

                # Forward pass
                activations, _ = self._forward(X_batch)
                X_recon = activations[-1]

                # Compute gradients of MSE Loss = 1/m * ||X - X_recon||^2
                dZ = (2.0 / m) * (X_recon - X_batch)
                grad_W = []
                grad_b = []

                # Backpropagate through layers
                for layer_idx in reversed(range(len(self.weights))):
                    A_prev = activations[layer_idx]
                    dW = np.dot(A_prev.T, dZ)
                    db = np.sum(dZ, axis=0)
                    grad_W.insert(0, dW)
                    grad_b.insert(0, db)

                    if layer_idx > 0:
                        dA_prev = np.dot(dZ, self.weights[layer_idx].T)
                        dZ = dA_prev * self._relu_deriv(activations[layer_idx])

                # Update parameters with momentum
                for idx in range(len(self.weights)):
                    v_W[idx] = momentum * v_W[idx] + self.learning_rate * grad_W[idx]
                    v_b[idx] = momentum * v_b[idx] + self.learning_rate * grad_b[idx]
                    self.weights[idx] -= v_W[idx]
                    self.biases[idx] -= v_b[idx]

        # Compute calibration threshold on training reconstructions
        recon_errors = self._compute_reconstruction_error(X_train)
        self.reconstruction_threshold = float(np.percentile(recon_errors, (1.0 - self.contamination) * 100))

        self.is_trained = True
        return self

    def _compute_reconstruction_error(self, X: np.ndarray) -> np.ndarray:
        if not self.weights:
            self._init_weights(X.shape[1])
            self.reconstruction_threshold = 1.0
        activations, _ = self._forward(X)
        X_recon = activations[-1]
        mse = np.mean((X - X_recon) ** 2, axis=1)
        return mse

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Map reconstruction error to a calibrated anomaly probability in [0, 1]."""
        n_samples = len(X)
        if not self.is_trained:
            default_scores = np.full(n_samples, 0.05, dtype=np.float64)
            return np.column_stack([1.0 - default_scores, default_scores])

        errors = self._compute_reconstruction_error(X)
        # Scaled sigmoid centered at reconstruction threshold
        scaled_diff = (errors - self.reconstruction_threshold) / (self.reconstruction_threshold + 1e-6)
        probs = 1.0 / (1.0 + np.exp(-np.clip(scaled_diff * 3.0, -10.0, 10.0)))
        return np.column_stack([1.0 - probs, probs])


