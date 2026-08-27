"""Unit tests for synthetic transaction generator and attack injection archetypes."""

import unittest
from datetime import datetime, timezone
from ml_engine.data.dataset_generator import SyntheticTransactionGenerator, generate_fraud_dataset


class TestSyntheticTransactionGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = SyntheticTransactionGenerator(seed=42)

    def test_single_legitimate_transaction(self):
        tx = self.generator.generate_single_transaction(
            timestamp=datetime.now(timezone.utc),
            force_fraud=False
        )
        self.assertIn("transaction_id", tx)
        self.assertEqual(tx["is_fraud"], 0)
        self.assertGreater(tx["amount"], 0.0)
        self.assertEqual(tx["fraud_archetype"], "LEGITIMATE")

    def test_all_fraud_archetypes(self):
        archetypes = [
            "CARD_TESTING", "ACCOUNT_TAKEOVER", "IMPOSSIBLE_TRAVEL",
            "CRYPTO_VELOCITY", "CREDENTIAL_STUFFING", "NOCTURNAL_LUXURY"
        ]
        for arch in archetypes:
            tx = self.generator.generate_single_transaction(
                timestamp=datetime.now(timezone.utc),
                force_fraud=True,
                fraud_archetype=arch
            )
            self.assertEqual(tx["is_fraud"], 1)
            self.assertEqual(tx["fraud_archetype"], arch)
            self.assertGreater(tx["amount"], 0.0)

    def test_dataset_generation_fraud_ratio(self):
        dataset = self.generator.generate_dataset(n_samples=200, fraud_ratio=0.10)
        self.assertEqual(len(dataset), 200)
        fraud_count = sum(1 for d in dataset if d["is_fraud"] == 1)
        self.assertEqual(fraud_count, 20)


if __name__ == "__main__":
    unittest.main()
