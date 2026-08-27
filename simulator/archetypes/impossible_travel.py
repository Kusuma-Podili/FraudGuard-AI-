"""Impossible Velocity Teleportation Attack Archetype.

Generates physical POS authorizations thousands of kilometers apart
within an unphysically short timeframe (>900 km/h).
"""

from typing import Dict, Any, List
import random
from datetime import datetime, timezone


class ImpossibleTravelArchetype:
    """Generates consecutive transactions in physically distant cities within minutes."""

    @staticmethod
    def generate_pair(card_id: str) -> List[Dict[str, Any]]:
        # Step 1: Legitimate transaction in New York (US)
        tx_ny = {
            "card_id": card_id,
            "cardholder_id": f"USR_{card_id[-5:]}",
            "amount": round(random.uniform(25.0, 85.0), 2),
            "currency": "USD",
            "merchant_id": "M_NYC_COFFEE_01",
            "merchant_name": "Manhattan Specialty Coffee",
            "merchant_category": "RESTAURANT",
            "entry_mode": "CHIP",
            "card_type": "CREDIT",
            "card_network": "MASTERCARD",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "country_code": "US",
            "ip_address": "64.233.160.1",
            "device_fingerprint": f"DEV_PHONE_{card_id[-4:]}",
            "failed_pin_attempts_24h": 0,
            "fraud_archetype": "LEGITIMATE",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Step 2: Fraudulent clone card transaction in Tokyo (Japan) 10 minutes later
        tx_tokyo = {
            "card_id": card_id,
            "cardholder_id": f"USR_{card_id[-5:]}",
            "amount": round(random.uniform(950.0, 3200.0), 2),
            "currency": "USD",
            "merchant_id": "M_TYO_CAMERA_09",
            "merchant_name": "Akihabara Super Electronics",
            "merchant_category": "ELECTRONICS",
            "entry_mode": "MAGSTRIPE",
            "card_type": "CREDIT",
            "card_network": "MASTERCARD",
            "latitude": 35.6762,
            "longitude": 139.6503,
            "country_code": "JP",
            "ip_address": "133.242.0.1",
            "device_fingerprint": f"DEV_POS_SKIMMER_99",
            "failed_pin_attempts_24h": 0,
            "fraud_archetype": "IMPOSSIBLE_TRAVEL",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        return [tx_ny, tx_tokyo]
