"""High-Throughput Async Transaction Simulation Engine.

Generates continuous streams of synthetic legitimate cardholder activity
interspersed with injected adversarial attack scenarios at configurable TPS.
"""

from __future__ import annotations
import asyncio
import random
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone

from ml_engine.data.dataset_generator import SyntheticTransactionGenerator
from simulator.archetypes import (
    CardTestingArchetype,
    ImpossibleTravelArchetype,
    AccountTakeoverArchetype,
    CryptoVelocityArchetype,
    CredentialStuffingArchetype,
    NocturnalLuxuryArchetype,
)


class TransactionSimulatorEngine:
    """Async streaming generator engine with attack wave injection."""

    def __init__(self, seed: int = 42, default_tps: int = 10):
        self.seed = seed
        self.tps = default_tps
        self.generator = SyntheticTransactionGenerator(seed=seed)
        self.is_running = False
        self.total_generated = 0
        self.active_attack: Optional[str] = None
        self._task: Optional[asyncio.Task] = None
        self._listeners: List[Callable[[Dict[str, Any]], None]] = []

    def register_listener(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register transaction consumer callback."""
        self._listeners.append(callback)

    def set_tps(self, tps: int) -> None:
        """Dynamically adjust throughput rate."""
        self.tps = max(1, min(tps, 500))

    def trigger_attack(self, attack_archetype: str) -> None:
        """Inject an attack archetype into subsequent transaction generation."""
        self.active_attack = attack_archetype

    def stop_attack(self) -> None:
        """Clear active attack archetype."""
        self.active_attack = None

    def generate_next_batch(self, count: int = 1) -> List[Dict[str, Any]]:
        """Generate synchronous batch of transactions."""
        batch = []
        now = datetime.now(timezone.utc)

        for _ in range(count):
            if self.active_attack == "CARD_TESTING":
                wave = CardTestingArchetype.generate_wave(card_id=f"CARD_TEST_{random.randint(100, 999)}", count=1)
                tx = wave[0]
            elif self.active_attack == "IMPOSSIBLE_TRAVEL":
                pair = ImpossibleTravelArchetype.generate_pair(card_id=f"CARD_TRAVEL_{random.randint(100, 999)}")
                tx = pair[1]
            elif self.active_attack == "ACCOUNT_TAKEOVER":
                burst = AccountTakeoverArchetype.generate_burst(card_id=f"CARD_ATO_{random.randint(100, 999)}", count=1)
                tx = burst[0]
            elif self.active_attack == "CRYPTO_VELOCITY":
                surge = CryptoVelocityArchetype.generate_surge(card_id=f"CARD_CRYPTO_{random.randint(100, 999)}", count=1)
                tx = surge[0]
            elif self.active_attack == "CREDENTIAL_STUFFING":
                attacks = CredentialStuffingArchetype.generate_attack(card_id=f"CARD_PIN_{random.randint(100, 999)}")
                tx = attacks[-1]
            elif self.active_attack == "NOCTURNAL_LUXURY":
                spree = NocturnalLuxuryArchetype.generate_spree(card_id=f"CARD_LUX_{random.randint(100, 999)}")
                tx = spree[0]
            else:
                # Organic traffic (mostly legitimate with 0.5% natural fraud)
                is_fraud = random.random() < 0.005
                tx = self.generator.generate_single_transaction(timestamp=now, force_fraud=is_fraud)

            self.total_generated += 1
            batch.append(tx)

        return batch

    async def start(self, duration_seconds: Optional[float] = None) -> None:
        """Start async simulation loop."""
        self.is_running = True
        start_t = time.time()

        while self.is_running:
            if duration_seconds and (time.time() - start_t) > duration_seconds:
                break

            interval = 1.0 / max(self.tps, 1)
            tx = self.generate_next_batch(count=1)[0]

            # Notify listeners
            for listener in self._listeners:
                try:
                    if asyncio.iscoroutinefunction(listener):
                        await listener(tx)
                    else:
                        listener(tx)
                except Exception as e:
                    print(f"Error notifying listener: {e}")

            await asyncio.sleep(interval)

        self.is_running = False

    def stop(self) -> None:
        """Halt simulation loop."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            self._task = None
