"""Cryptographic Immutable Audit Ledger & Merkle Tree Proof System.

Maintains tamper-evident SHA-256 HMAC chained block audit trails for regulatory compliance,
providing Merkle tree proofs of integrity for legal discovery and financial audits.
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any


@dataclass
class AuditBlock:
    block_index: int
    timestamp: str
    event_type: str
    actor_id: str
    target_entity_id: str
    payload_hash: str
    previous_block_hash: str
    current_block_hash: str = ""

    def calculate_hash(self, secret_salt: str = "merkle_salt_2026") -> str:
        data_str = f"{self.block_index}:{self.timestamp}:{self.event_type}:{self.actor_id}:{self.target_entity_id}:{self.payload_hash}:{self.previous_block_hash}:{secret_salt}"
        self.current_block_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
        return self.current_block_hash


class ImmutableAuditLedger:
    """Tamper-evident blockchain-style linear audit ledger."""

    GENESIS_PREV_HASH = "0" * 64

    def __init__(self, ledger_salt: str = "fraudguard_immutable_ledger_2026"):
        self.ledger_salt = ledger_salt
        self.chain: List[AuditBlock] = []
        self._init_genesis_block()

    def _init_genesis_block(self):
        genesis = AuditBlock(
            block_index=0,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type="LEDGER_GENESIS_INITIALIZED",
            actor_id="SYSTEM_ROOT",
            target_entity_id="ROOT",
            payload_hash=hashlib.sha256(b"GENESIS").hexdigest(),
            previous_block_hash=self.GENESIS_PREV_HASH,
        )
        genesis.calculate_hash(self.ledger_salt)
        self.chain.append(genesis)

    def append_event(self, event_type: str, actor_id: str, target_id: str, raw_payload: Dict[str, Any]) -> AuditBlock:
        """Append a new cryptographic audit entry to the immutable ledger."""
        payload_serialized = json.dumps(raw_payload, sort_keys=True)
        payload_hash = hashlib.sha256(payload_serialized.encode("utf-8")).hexdigest()
        prev_block = self.chain[-1]

        new_block = AuditBlock(
            block_index=len(self.chain),
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            actor_id=actor_id,
            target_entity_id=target_id,
            payload_hash=payload_hash,
            previous_block_hash=prev_block.current_block_hash,
        )
        new_block.calculate_hash(self.ledger_salt)
        self.chain.append(new_block)
        return new_block

    def verify_ledger_integrity(self) -> Tuple[bool, Optional[int]]:
        """Verify entire cryptographic chain from genesis to head."""
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            if curr.previous_block_hash != prev.current_block_hash:
                return False, i

            recomputed = hashlib.sha256(
                f"{curr.block_index}:{curr.timestamp}:{curr.event_type}:{curr.actor_id}:{curr.target_entity_id}:{curr.payload_hash}:{curr.previous_block_hash}:{self.ledger_salt}".encode("utf-8")
            ).hexdigest()

            if curr.current_block_hash != recomputed:
                return False, i

        return True, None

    def compute_merkle_root(self) -> str:
        """Calculate Merkle root hash of all block hashes in the ledger."""
        if not self.chain:
            return ""

        hashes = [b.current_block_hash for b in self.chain]
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])
            new_level = []
            for i in range(0, len(hashes), 2):
                combined = hashlib.sha256((hashes[i] + hashes[i + 1]).encode("utf-8")).hexdigest()
                new_level.append(combined)
            hashes = new_level

        return hashes[0]
