"""Unit tests for Transaction Record Schemas and Validation."""

import unittest
from backend.app.schemas.transaction import TransactionEvaluationRequest


class TestTransactionSchemas(unittest.TestCase):

    def test_valid_transaction_schema(self):
        req = TransactionEvaluationRequest(
            card_id="CARD_123456",
            amount=150.75,
            merchant_id="M_AMZN_01",
            merchant_category="E_COMMERCE"
        )
        self.assertEqual(req.amount, 150.75)
        self.assertEqual(req.currency, "USD")

    def test_negative_amount_validation(self):
        with self.assertRaises(ValueError):
            TransactionEvaluationRequest(
                card_id="CARD_123456",
                amount=-10.0,
                merchant_id="M_AMZN_01"
            )


if __name__ == "__main__":
    unittest.main()
