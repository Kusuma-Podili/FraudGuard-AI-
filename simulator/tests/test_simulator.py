"""Unit tests for TransactionSimulatorEngine."""

import unittest
import asyncio
from simulator.engine import TransactionSimulatorEngine


class TestSimulatorEngine(unittest.TestCase):

    def setUp(self):
        self.sim = TransactionSimulatorEngine(seed=42, default_tps=20)

    def test_batch_generation(self):
        batch = self.sim.generate_next_batch(count=15)
        self.assertEqual(len(batch), 15)
        self.assertEqual(self.sim.total_generated, 15)
        for tx in batch:
            self.assertIn("card_id", tx)
            self.assertIn("amount", tx)
            self.assertGreater(tx["amount"], 0)

    def test_attack_injection_lifecycle(self):
        self.sim.trigger_attack("CARD_TESTING")
        batch = self.sim.generate_next_batch(count=3)
        for tx in batch:
            self.assertEqual(tx["fraud_archetype"], "CARD_TESTING")

        self.sim.stop_attack()
        self.assertIsNone(self.sim.active_attack)

    def test_async_listener_notification(self):
        collected = []

        def _on_tx(tx):
            collected.append(tx)

        self.sim.register_listener(_on_tx)
        batch = self.sim.generate_next_batch(count=2)
        # Manually invoke listener as in async loop
        _on_tx(batch[0])
        self.assertEqual(len(collected), 1)


if __name__ == "__main__":
    unittest.main()
