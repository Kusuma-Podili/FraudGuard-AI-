"""Multi-Head Self-Attention Sequential Transformer for Credit Card Fraud Detection.

Implements `FraudTransformerNet` with:
- Sinusoidal & Learned Positional Temporal Encodings
- Scaled Dot-Product Multi-Head Self-Attention layers
- Multi-Layer Perceptron (MLP) Feed-Forward sub-layers with GELU activations
- Layer Normalization and Residual Skip Connections
- Sequence-level classification head for temporal transaction histories
"""

from __future__ import annotations
import math
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


class PositionalEncoding:
    """Calculates sinusoidal positional embeddings for temporal transaction order."""

    def __init__(self, d_model: int, max_len: int = 50):
        self.d_model = d_model
        self.max_len = max_len
        self.pe = np.zeros((max_len, d_model), dtype=np.float32)

        position = np.arange(0, max_len, dtype=np.float32)[:, np.newaxis]
        div_term = np.exp(np.arange(0, d_model, 2, dtype=np.float32) * -(math.log(10000.0) / d_model))

        self.pe[:, 0::2] = np.sin(position * div_term)
        self.pe[:, 1::2] = np.cos(position * div_term)

    def get_embedding(self, seq_len: int) -> np.ndarray:
        return self.pe[:seq_len, :]


class MultiHeadAttention:
    """Scaled Dot-Product Multi-Head Self-Attention Sublayer."""

    def __init__(self, d_model: int = 64, num_heads: int = 4, seed: int = 42):
        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        rng = np.random.RandomState(seed)
        # Weight matrices for Q, K, V, and Output projection
        self.w_q = rng.randn(d_model, d_model).astype(np.float32) * 0.05
        self.w_k = rng.randn(d_model, d_model).astype(np.float32) * 0.05
        self.w_v = rng.randn(d_model, d_model).astype(np.float32) * 0.05
        self.w_o = rng.randn(d_model, d_model).astype(np.float32) * 0.05

        self.last_attention_weights: Optional[np.ndarray] = None

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass for sequence tensor of shape (seq_len, d_model)."""
        seq_len, _ = x.shape

        # Linear projections
        q = np.dot(x, self.w_q)  # (seq_len, d_model)
        k = np.dot(x, self.w_k)
        v = np.dot(x, self.w_v)

        # Reshape to (num_heads, seq_len, d_k)
        q_heads = q.reshape(seq_len, self.num_heads, self.d_k).swapaxes(0, 1)
        k_heads = k.reshape(seq_len, self.num_heads, self.d_k).swapaxes(0, 1)
        v_heads = v.reshape(seq_len, self.num_heads, self.d_k).swapaxes(0, 1)

        # Scaled dot-product: (Q * K^T) / sqrt(d_k)
        scores = np.matmul(q_heads, k_heads.swapaxes(-1, -2)) / math.sqrt(self.d_k)

        # Softmax over last dimension
        exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        attn_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
        self.last_attention_weights = attn_weights

        # Multiply with V: (num_heads, seq_len, d_k)
        context = np.matmul(attn_weights, v_heads)

        # Concatenate heads: (seq_len, d_model)
        concat = context.swapaxes(0, 1).reshape(seq_len, self.d_model)

        # Final linear projection
        out = np.dot(concat, self.w_o)
        return out


class TransformerEncoderLayer:
    """Single Transformer Encoder Block with Multi-Head Attention, MLP, and LayerNorm."""

    def __init__(self, d_model: int = 64, num_heads: int = 4, d_ff: int = 128, seed: int = 42):
        self.mha = MultiHeadAttention(d_model=d_model, num_heads=num_heads, seed=seed)
        rng = np.random.RandomState(seed + 1)
        self.w1 = rng.randn(d_model, d_ff).astype(np.float32) * 0.05
        self.b1 = np.zeros(d_ff, dtype=np.float32)
        self.w2 = rng.randn(d_ff, d_model).astype(np.float32) * 0.05
        self.b2 = np.zeros(d_model, dtype=np.float32)

    @staticmethod
    def gelu(x: np.ndarray) -> np.ndarray:
        return 0.5 * x * (1.0 + np.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * np.power(x, 3))))

    @staticmethod
    def layer_norm(x: np.ndarray, eps: float = 1e-5) -> np.ndarray:
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        return (x - mean) / np.sqrt(var + eps)

    def forward(self, x: np.ndarray) -> np.ndarray:
        # Sub-layer 1: Multi-Head Attention with Residual & Norm
        attn_out = self.mha.forward(x)
        x = self.layer_norm(x + attn_out)

        # Sub-layer 2: Feed-Forward MLP with GELU & Norm
        ff_hidden = self.gelu(np.dot(x, self.w1) + self.b1)
        ff_out = np.dot(ff_hidden, self.w2) + self.b2
        x = self.layer_norm(x + ff_out)

        return x


class FraudTransformerNet:
    """Full Sequential Transformer for analyzing cardholder transaction trajectory sequences."""

    def __init__(self, input_dim: int = 16, d_model: int = 64, num_heads: int = 4, num_layers: int = 2, seed: int = 42):
        self.input_dim = input_dim
        self.d_model = d_model
        rng = np.random.RandomState(seed)

        # Input feature projection to d_model
        self.input_projection = rng.randn(input_dim, d_model).astype(np.float32) * 0.1
        self.pos_encoder = PositionalEncoding(d_model=d_model)

        # Stacked Transformer Encoder layers
        self.layers = [
            TransformerEncoderLayer(d_model=d_model, num_heads=num_heads, seed=seed + i * 10)
            for i in range(num_layers)
        ]

        # Classification Head
        self.classifier_w = rng.randn(d_model, 1).astype(np.float32) * 0.1
        self.classifier_b = np.zeros(1, dtype=np.float32)

    def predict_sequence_risk(self, sequence_features: np.ndarray) -> Tuple[float, np.ndarray]:
        """Predict fraud probability on historical sequence (seq_len, input_dim)."""
        seq_len, _ = sequence_features.shape
        x = np.dot(sequence_features, self.input_projection)
        x = x + self.pos_encoder.get_embedding(seq_len)

        for layer in self.layers:
            x = layer.forward(x)

        # Global average pooling over sequence length
        pooled = np.mean(x, axis=0, keepdims=True)  # (1, d_model)
        logit = np.dot(pooled, self.classifier_w) + self.classifier_b
        prob = 1.0 / (1.0 + np.exp(-logit[0, 0]))

        attention_map = self.layers[-1].mha.last_attention_weights
        return float(prob), attention_map
