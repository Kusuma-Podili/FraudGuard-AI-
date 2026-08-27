"""Bipartite Graph Network Analytics and Fraud Ring Syndicate Detector.

Constructs multi-entity bipartite graph topologies linking Cardholders,
Device Fingerprints, IP Addresses, and Merchant Terminals to uncover organized
credit card fraud rings, card-sharing syndicates, and mule networks.
"""

from __future__ import annotations
import collections
from typing import Dict, Any, List, Set, Tuple, Optional
import numpy as np


class FraudGraphNetworkDetector:
    """Graph mining engine detecting cyclic topologies, dense clusters, and shared entities."""

    def __init__(self, high_degree_threshold: int = 4):
        self.high_degree_threshold = high_degree_threshold
        # Adjacency maps
        self.card_to_devices: Dict[str, Set[str]] = collections.defaultdict(set)
        self.device_to_cards: Dict[str, Set[str]] = collections.defaultdict(set)
        self.card_to_ips: Dict[str, Set[str]] = collections.defaultdict(set)
        self.ip_to_cards: Dict[str, Set[str]] = collections.defaultdict(set)
        self.card_to_merchants: Dict[str, Set[str]] = collections.defaultdict(set)

    def add_edge(self, card_id: str, device_id: str = "", ip_address: str = "", merchant_id: str = "") -> None:
        """Register graph edges between entities."""
        if device_id:
            self.card_to_devices[card_id].add(device_id)
            self.device_to_cards[device_id].add(card_id)
        if ip_address:
            self.card_to_ips[card_id].add(ip_address)
            self.ip_to_cards[ip_address].add(card_id)
        if merchant_id:
            self.card_to_merchants[card_id].add(merchant_id)

    def compute_ring_risk_score(self, card_id: str, device_id: str = "", ip_address: str = "") -> Tuple[float, Dict[str, Any]]:
        """Calculate graph-based syndicate risk score in [0.0, 1.0]."""
        associated_cards_by_device: Set[str] = set()
        associated_cards_by_ip: Set[str] = set()

        if device_id and device_id in self.device_to_cards:
            associated_cards_by_device = self.device_to_cards[device_id] - {card_id}

        if ip_address and ip_address in self.ip_to_cards:
            associated_cards_by_ip = self.ip_to_cards[ip_address] - {card_id}

        total_shared_cards = len(associated_cards_by_device.union(associated_cards_by_ip))
        card_device_count = len(self.card_to_devices.get(card_id, set()))
        card_ip_count = len(self.card_to_ips.get(card_id, set()))

        # Exponential scaling for shared entities
        risk_score = 0.0
        if total_shared_cards >= 5:
            risk_score = 0.95
        elif total_shared_cards >= 3:
            risk_score = 0.75
        elif total_shared_cards >= 1:
            risk_score = 0.35
        elif card_device_count > 6 or card_ip_count > 10:
            risk_score = 0.40
        else:
            risk_score = 0.02

        telemetry = {
            "card_id": card_id,
            "shared_cards_count": total_shared_cards,
            "device_degree": len(associated_cards_by_device),
            "ip_degree": len(associated_cards_by_ip),
            "card_unique_devices": card_device_count,
            "card_unique_ips": card_ip_count,
            "is_potential_fraud_ring": total_shared_cards >= self.high_degree_threshold,
            "graph_risk_score": round(risk_score, 4)
        }

        return risk_score, telemetry

    def find_connected_syndicate(self, root_card: str, max_depth: int = 2) -> List[str]:
        """Perform breadth-first search (BFS) to identify full entity cluster around a card."""
        visited_cards: Set[str] = {root_card}
        queue: collections.deque[Tuple[str, int]] = collections.deque([(root_card, 0)])

        while queue:
            curr_card, depth = queue.popleft()
            if depth >= max_depth:
                continue

            # Traverse through devices
            for dev in self.card_to_devices.get(curr_card, set()):
                for neighbor_card in self.device_to_cards.get(dev, set()):
                    if neighbor_card not in visited_cards:
                        visited_cards.add(neighbor_card)
                        queue.append((neighbor_card, depth + 1))

            # Traverse through IPs
            for ip in self.card_to_ips.get(curr_card, set()):
                for neighbor_card in self.ip_to_cards.get(ip, set()):
                    if neighbor_card not in visited_cards:
                        visited_cards.add(neighbor_card)
                        queue.append((neighbor_card, depth + 1))

        return list(visited_cards)
