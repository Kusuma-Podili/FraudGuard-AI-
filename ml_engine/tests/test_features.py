"""Unit tests for Geodistance, Velocity Engine, and Feature Store."""

import unittest
from datetime import datetime, timezone, timedelta
from ml_engine.data.geodistance import calculate_haversine_distance, is_impossible_travel
from ml_engine.data.velocity_engine import VelocityEngine
from ml_engine.data.feature_store import FeatureStore


class TestFeatureEngineering(unittest.TestCase):

    def test_haversine_known_distances(self):
        # London to Paris is ~343 km
        london_lat, london_lon = 51.5074, -0.1278
        paris_lat, paris_lon = 48.8566, 2.3522
        dist = calculate_haversine_distance(london_lat, london_lon, paris_lat, paris_lon)
        self.assertAlmostEqual(dist, 343.0, delta=10.0)

    def test_impossible_travel_detection(self):
        t1 = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        # New York
        ny_lat, ny_lon = 40.7128, -74.0060

        # Tokyo 30 minutes later (Impossible speed ~21,700 km/h)
        t2 = datetime(2026, 1, 1, 10, 30, 0, tzinfo=timezone.utc)
        tokyo_lat, tokyo_lon = 35.6762, 139.6503

        impossible, telem = is_impossible_travel(ny_lat, ny_lon, t1, tokyo_lat, tokyo_lon, t2)
        self.assertTrue(impossible)
        self.assertGreater(telem["velocity_kmh"], 5000.0)

    def test_velocity_sliding_windows(self):
        engine = VelocityEngine()
        now = datetime.now(timezone.utc).timestamp()
        card = "CARD_TEST_001"

        # Record 5 transactions in 10 minutes
        for i in range(5):
            engine.record_event(card_id=card, amount=50.0, timestamp_epoch=now - (i * 100))

        features = engine.extract_velocity_features(card_id=card, current_amount=100.0, timestamp_epoch=now)
        self.assertEqual(features["velocity_1h"], 5)
        self.assertEqual(features["velocity_24h"], 5)

    def test_feature_store_enrichment(self):
        store = FeatureStore()
        raw_tx = {
            "card_id": "CARD_FS_999",
            "amount": 250.0,
            "merchant_id": "M_AMZN_01",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "country_code": "US",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        enriched = store.enrich_transaction(raw_tx)
        self.assertIn("distance_from_home_km", enriched)
        self.assertIn("velocity_1h", enriched)
        self.assertIn("is_foreign_transaction", enriched)


if __name__ == "__main__":
    unittest.main()
