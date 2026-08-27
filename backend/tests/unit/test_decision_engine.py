"""Unit tests for Real-Time Decision Engine."""

import unittest
from backend.app.services.decision_engine import DecisionEngine


class TestDecisionEngineUnit(unittest.TestCase):

    def setUp(self):
        self.engine = DecisionEngine()

    def test_legitimate_transaction_scoring(self):
        raw_tx = {
            "card_id": "CARD_TEST_101",
            "amount": 35.50,
            "merchant_id": "M_WMT_02",
            "merchant_category": "GROCERY",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "country_code": "US",
            "failed_pin_attempts_24h": 0
        }
        res = self.engine.evaluate_transaction(raw_tx)
        self.assertIn("decision_action", res)
        self.assertIn("risk_score", res)
        self.assertIn("latency_ms", res)
        self.assertLess(res["latency_ms"], 100.0)  # Sub-100ms in unit test
        self.assertEqual(res["decision_action"], "ALLOW")

    def test_brute_force_failed_pin_triggers_decline(self):
        raw_tx = {
            "card_id": "CARD_TEST_102",
            "amount": 150.0,
            "merchant_id": "M_AMZN_01",
            "failed_pin_attempts_24h": 4
        }
        res = self.engine.evaluate_transaction(raw_tx)
        self.assertEqual(res["decision_action"], "DECLINE")
        self.assertGreaterEqual(res["risk_score"], 0.85)


if __name__ == "__main__":
    unittest.main()
