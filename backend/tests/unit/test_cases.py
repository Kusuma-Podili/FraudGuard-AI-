"""Unit tests for Case Model and Severity Calculation."""

import unittest
from backend.app.models.case import InvestigationCase, CaseSeverity, CaseStatus


class TestCaseUnit(unittest.TestCase):

    def test_case_creation_and_defaults(self):
        case = InvestigationCase(
            case_number="CASE-2026-TEST01",
            transaction_id="TX_1001",
            card_id="CARD_999",
            cardholder_id="USR_999",
            amount=4200.0,
            risk_score=0.91,
            severity=CaseSeverity.CRITICAL,
            status=CaseStatus.OPEN
        )
        self.assertEqual(case.case_number, "CASE-2026-TEST01")
        self.assertEqual(case.severity, CaseSeverity.CRITICAL)
        self.assertEqual(case.status, CaseStatus.OPEN)


if __name__ == "__main__":
    unittest.main()
