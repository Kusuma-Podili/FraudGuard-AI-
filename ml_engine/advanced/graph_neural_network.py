"""Graph Convolutional Network (GCN) & Graph Attention Network (GAT) for Fraud Syndicates.

Performs relational node embedding aggregation across bipartite cardholder-device-merchant graphs
using symmetric normalized Laplacian convolution and multi-head attention message passing.
"""

from __future__ import annotations
import numpy as np
from typing import Dict, List, Optional, Tuple, Any


class GraphConvolutionLayer:
    """Spectral Graph Convolution Layer with Renormalization Trick (Kipf & Welling)."""

    def __init__(self, in_features: int, out_features: int, seed: int = 42):
        self.in_features = in_features
        self.out_features = out_features
        rng = np.random.RandomState(seed)
        self.weight = rng.randn(in_features, out_features).astype(np.float32) * np.sqrt(2.0 / in_features)
        self.bias = np.zeros(out_features, dtype=np.float32)

    @staticmethod
    def normalize_adjacency(adj: np.ndarray) -> np.ndarray:
        """Compute D^-1/2 * (A + I) * D^-1/2."""
        num_nodes = adj.shape[0]
        adj_tilde = adj + np.eye(num_nodes, dtype=np.float32)
        degree = np.sum(adj_tilde, axis=1)
        deg_inv_sqrt = np.power(np.maximum(degree, 1e-12), -0.5)
        d_mat_inv_sqrt = np.diag(deg_inv_sqrt)
        return np.dot(np.dot(d_mat_inv_sqrt, adj_tilde), d_mat_inv_sqrt)

    def forward(self, x: np.ndarray, norm_adj: np.ndarray) -> np.ndarray:
        """Forward pass: ReLU(norm_adj * X * W + b)."""
        support = np.dot(x, self.weight)
        output = np.dot(norm_adj, support) + self.bias
        return np.maximum(0.0, output)  # ReLU


class GraphAttentionLayer:
    """Graph Attention Network (GAT) Layer with LeakyReLU Attention Coefficients (Veličković et al.)."""

    def __init__(self, in_features: int, out_features: int, alpha: float = 0.2, seed: int = 42):
        self.in_features = in_features
        self.out_features = out_features
        self.alpha = alpha
        rng = np.random.RandomState(seed)
        self.weight = rng.randn(in_features, out_features).astype(np.float32) * np.sqrt(2.0 / in_features)
        self.a = rng.randn(2 * out_features, 1).astype(np.float32) * 0.1

    def forward(self, x: np.ndarray, adj: np.ndarray) -> np.ndarray:
        """Compute node attention coefficients and propagate messages."""
        num_nodes = x.shape[0]
        h = np.dot(x, self.weight)  # (N, out_features)

        # Pairwise concatenation for attention mechanism
        h_i = np.repeat(h, num_nodes, axis=0)
        h_j = np.tile(h, (num_nodes, 1))
        concat = np.concatenate([h_i, h_j], axis=-1)  # (N*N, 2*out_features)

        e_raw = np.dot(concat, self.a).reshape(num_nodes, num_nodes)
        # LeakyReLU
        e = np.where(e_raw > 0, e_raw, e_raw * self.alpha)

        # Mask non-adjacent nodes with -inf before softmax
        mask = (adj + np.eye(num_nodes)) > 0
        e_masked = np.where(mask, e, -1e9)

        # Softmax over neighborhood
        exp_e = np.exp(e_masked - np.max(e_masked, axis=-1, keepdims=True))
        attention_weights = exp_e / np.sum(exp_e, axis=-1, keepdims=True)

        out = np.dot(attention_weights, h)
        return np.maximum(0.0, out)


class FraudGraphNeuralNetwork:
    """Full 2-layer GCN/GAT pipeline for detecting complex syndicate fraud rings."""

    def __init__(self, num_features: int = 8, hidden_dim: int = 16, seed: int = 42):
        self.gcn1 = GraphConvolutionLayer(in_features=num_features, out_features=hidden_dim, seed=seed)
        self.gat2 = GraphAttentionLayer(in_features=hidden_dim, out_features=hidden_dim, seed=seed + 1)
        rng = np.random.RandomState(seed + 2)
        self.classifier_w = rng.randn(hidden_dim, 1).astype(np.float32) * 0.1
        self.classifier_b = np.zeros(1, dtype=np.float32)

    def predict_node_risk(self, node_features: np.ndarray, adjacency_matrix: np.ndarray) -> np.ndarray:
        """Score each node's fraud syndicate probability given graph topology."""
        norm_adj = GraphConvolutionLayer.normalize_adjacency(adjacency_matrix)
        h1 = self.gcn1.forward(node_features, norm_adj)
        h2 = self.gat2.forward(h1, adjacency_matrix)

        logits = np.dot(h2, self.classifier_w) + self.classifier_b
        probs = 1.0 / (1.0 + np.exp(-logits))
        return probs.flatten()
