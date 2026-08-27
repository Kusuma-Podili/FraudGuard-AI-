"""Unit tests for AST Safe Rule Evaluator."""

import unittest
from backend.app.services.rule_evaluator import SafeRuleEvaluator


class TestRuleEvaluator(unittest.TestCase):

    def test_basic_comparisons(self):
        ctx = {"amount": 5500.0, "velocity_1h": 4}
        is_match, vars_matched = SafeRuleEvaluator.evaluate_expression("amount > 5000.0", ctx)
        self.assertTrue(is_match)
        self.assertEqual(vars_matched["amount"], 5500.0)

    def test_complex_boolean_logic(self):
        ctx = {
            "amount": 3200.0,
            "velocity_1h": 5,
            "failed_pin_attempts_24h": 0,
            "merchant_category": "ELECTRONICS"
        }
        expr = "amount > 2000.0 AND velocity_1h >= 4 AND merchant_category == 'ELECTRONICS'"
        is_match, _ = SafeRuleEvaluator.evaluate_expression(expr, ctx)
        self.assertTrue(is_match)

    def test_unmatched_expression(self):
        ctx = {"amount": 50.0, "velocity_1h": 1}
        is_match, _ = SafeRuleEvaluator.evaluate_expression("amount > 1000.0", ctx)
        self.assertFalse(is_match)


if __name__ == "__main__":
    unittest.main()
