"""Integration tests for FastAPI REST endpoints using Starlette TestClient."""

import unittest
from starlette.testclient import TestClient
from backend.app.main import app


class TestAPIEndpointsIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client_context = TestClient(app)
        cls.client = cls.client_context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client_context.__exit__(None, None, None)

    def test_health_check_endpoint(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["data"]["status"], "ONLINE")


    def test_real_time_scoring_endpoint(self):
        payload = {
            "card_id": "CARD_INT_001",
            "amount": 85.0,
            "merchant_id": "M_AMZN_01",
            "merchant_category": "E_COMMERCE",
            "country_code": "US"
        }
        response = self.client.post("/api/v1/transactions/score", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("decision_action", data["data"])
        self.assertIn("risk_score", data["data"])
        self.assertIn("latency_ms", data["data"])

    def _get_auth_headers(self) -> dict:
        login_resp = self.client.post(
            "/api/v1/auth/login/json",
            json={"email": "admin@fraudguard.ai", "password": "Admin@FraudGuard2026"}
        )
        token = login_resp.json()["data"]["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_rule_dry_run_endpoint(self):
        headers = self._get_auth_headers()
        payload = {
            "condition_expression": "amount > 1000.0 AND velocity_1h >= 2",
            "sample_transaction": {
                "amount": 1500.0,
                "velocity_1h": 3
            }
        }
        response = self.client.post("/api/v1/rules/dry-run", json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["data"]["is_triggered"])

    def test_simulation_status_endpoint(self):
        headers = self._get_auth_headers()
        response = self.client.get("/api/v1/simulation/status", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("is_running", data["data"])



if __name__ == "__main__":
    unittest.main()
