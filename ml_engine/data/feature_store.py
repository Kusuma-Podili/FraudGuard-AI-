"""Unified Online/Offline Feature Store for Real-Time Inference and Training.

Manages entity states (Cardholders, Merchants, Devices, Geo Locations),
sliding-window velocity lookups, and feature vector assembly for sub-20ms model inference.
"""

from __future__ import annotations
import math
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
import numpy as np

from ml_engine.data.geodistance import calculate_haversine_distance, is_impossible_travel
from ml_engine.data.velocity_engine import VelocityEngine
from ml_engine.data.preprocessors import TabularPreprocessor
from ml_engine.data.feature_registry import default_registry, FeatureRegistry


class FeatureStore:
    """Enterprise Feature Store managing entity profiles and real-time state."""

    def __init__(self, registry: Optional[FeatureRegistry] = None):
        self.registry = registry or default_registry
        self.velocity_engine = VelocityEngine()
        self.preprocessor = TabularPreprocessor()

        # In-memory entity profiles
        self._cardholder_profiles: Dict[str, Dict[str, Any]] = {}
        self._merchant_profiles: Dict[str, Dict[str, Any]] = {}
        self._last_transaction_geo: Dict[str, Tuple[float, float, datetime]] = {}

        # Default static baselines
        self._initialize_default_profiles()

    def _initialize_default_profiles(self) -> None:
        """Seed default merchant categories and baseline profiles."""
        self._merchant_profiles = {
            "M_AMAZON_US": {"risk_score": 0.05, "category": "E_COMMERCE", "country": "US", "avg_ticket": 45.50},
            "M_APPLE_STORE": {"risk_score": 0.08, "category": "ELECTRONICS", "country": "US", "avg_ticket": 320.00},
            "M_CRYPTO_BINANCE": {"risk_score": 0.65, "category": "CRYPTO_EXCHANGE", "country": "KY", "avg_ticket": 1250.00},
            "M_LUXURY_ROLEX": {"risk_score": 0.42, "category": "LUXURY_JEWELRY", "country": "CH", "avg_ticket": 4500.00},
            "M_WALMART_POS": {"risk_score": 0.03, "category": "GROCERY", "country": "US", "avg_ticket": 68.20},
            "M_CASINO_BELLAGIO": {"risk_score": 0.58, "category": "GAMBLING", "country": "US", "avg_ticket": 850.00},
            "M_DELTA_AIRLINES": {"risk_score": 0.15, "category": "TRAVEL_AIRLINE", "country": "US", "avg_ticket": 480.00},
            "M_SHELL_GAS": {"risk_score": 0.12, "category": "GAS_STATION", "country": "US", "avg_ticket": 52.00},
        }

    def register_cardholder(
        self,
        card_id: str,
        cardholder_id: str,
        home_lat: float,
        home_lon: float,
        home_country: str = "US",
        age: int = 35,
        avg_30d_amount: float = 65.00
    ) -> None:
        """Register or update static cardholder baseline."""
        self._cardholder_profiles[card_id] = {
            "cardholder_id": cardholder_id,
            "home_lat": home_lat,
            "home_lon": home_lon,
            "home_country": home_country,
            "cardholder_age": age,
            "avg_30d_amount": avg_30d_amount,
            "registered_at": datetime.now(timezone.utc),
        }

    def register_merchant(
        self,
        merchant_id: str,
        category: str,
        risk_score: float,
        country: str = "US",
        avg_ticket: float = 50.0
    ) -> None:
        """Register or update merchant profile."""
        self._merchant_profiles[merchant_id] = {
            "category": category,
            "risk_score": risk_score,
            "country": country,
            "avg_ticket": avg_ticket,
        }

    def enrich_transaction(self, raw_tx: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a raw transaction payload with online feature store attributes."""
        card_id = str(raw_tx.get("card_id", "CARD_DEFAULT"))
        merchant_id = str(raw_tx.get("merchant_id", "M_GENERAL"))
        amount = float(raw_tx.get("amount", 0.0))
        tx_lat = float(raw_tx.get("latitude", 37.7749))
        tx_lon = float(raw_tx.get("longitude", -122.4194))
        tx_time_raw = raw_tx.get("timestamp")

        if isinstance(tx_time_raw, str):
            try:
                tx_time = datetime.fromisoformat(tx_time_raw.replace("Z", "+00:00"))
            except ValueError:
                tx_time = datetime.now(timezone.utc)
        elif isinstance(tx_time_raw, datetime):
            tx_time = tx_time_raw
        else:
            tx_time = datetime.now(timezone.utc)

        epoch_seconds = tx_time.timestamp()
        ip_addr = str(raw_tx.get("ip_address", "127.0.0.1"))
        device_fp = str(raw_tx.get("device_fingerprint", "DEV_DEFAULT"))

        # 1. Retrieve Cardholder Profile
        card_profile = self._cardholder_profiles.get(card_id, {
            "home_lat": 37.7749,
            "home_lon": -122.4194,
            "home_country": "US",
            "cardholder_age": 35,
            "avg_30d_amount": 75.0,
        })

        # 2. Geodesic distance to home
        dist_home = calculate_haversine_distance(
            tx_lat, tx_lon, card_profile["home_lat"], card_profile["home_lon"]
        )

        # 3. Impossible Travel Velocity Check (vs last known transaction location)
        is_teleportation = False
        travel_velocity_kmh = 0.0
        if card_id in self._last_transaction_geo:
            prev_lat, prev_lon, prev_time = self._last_transaction_geo[card_id]
            is_teleportation, telemetry = is_impossible_travel(
                prev_lat, prev_lon, prev_time, tx_lat, tx_lon, tx_time
            )
            travel_velocity_kmh = telemetry["velocity_kmh"]

        # 4. Extract Real-Time Sliding-Window Velocity
        velocity_data = self.velocity_engine.extract_velocity_features(
            card_id=card_id,
            current_amount=amount,
            timestamp_epoch=epoch_seconds,
            ip_address=ip_addr,
            device_fingerprint=device_fp
        )

        # 5. Merchant Risk Lookup
        merchant_prof = self._merchant_profiles.get(merchant_id, {
            "category": raw_tx.get("merchant_category", "GENERAL_RETAIL"),
            "risk_score": 0.10,
            "country": raw_tx.get("country_code", "US"),
            "avg_ticket": 50.0,
        })

        # 6. Temporal Features
        hour_of_day = tx_time.hour + (tx_time.minute / 60.0)
        day_of_week = float(tx_time.weekday())

        # Assemble unified feature dictionary
        enriched: Dict[str, Any] = {
            **raw_tx,
            "cardholder_age": card_profile["cardholder_age"],
            "distance_from_home_km": round(dist_home, 2),
            "is_impossible_travel": is_teleportation,
            "travel_velocity_kmh": round(travel_velocity_kmh, 2),
            "merchant_category": merchant_prof["category"],
            "merchant_historical_risk": merchant_prof["risk_score"],
            "hour_of_day": round(hour_of_day, 2),
            "day_of_week": int(day_of_week),
            "velocity_1h": velocity_data["velocity_1h"],
            "velocity_24h": velocity_data["velocity_24h"],
            "velocity_5m": velocity_data["velocity_5m"],
            "amount_ratio_to_mean_30d": round(
                amount / max(card_profile["avg_30d_amount"], 1.0), 4
            ),
            "failed_pin_attempts_24h": int(raw_tx.get("failed_pin_attempts_24h", 0)),
            "is_foreign_transaction": (raw_tx.get("country_code", "US") != card_profile["home_country"]),
        }

        # Update in-memory state after observation
        self._last_transaction_geo[card_id] = (tx_lat, tx_lon, tx_time)
        self.velocity_engine.record_event(
            card_id=card_id,
            amount=amount,
            timestamp_epoch=epoch_seconds,
            merchant_id=merchant_id,
            country=raw_tx.get("country_code", "US"),
            device_fingerprint=device_fp,
            ip_address=ip_addr
        )

        return enriched

    def get_feature_vector(self, enriched_tx: Dict[str, Any]) -> np.ndarray:
        """Transform enriched dictionary into numeric feature vector for model scoring."""
        return self.preprocessor.transform_single(enriched_tx)


# Singleton instance
_GLOBAL_FEATURE_STORE: Optional[FeatureStore] = None


def get_feature_store() -> FeatureStore:
    """Retrieve or initialize the global singleton feature store."""
    global _GLOBAL_FEATURE_STORE
    if _GLOBAL_FEATURE_STORE is None:
        _GLOBAL_FEATURE_STORE = FeatureStore()
    return _GLOBAL_FEATURE_STORE
