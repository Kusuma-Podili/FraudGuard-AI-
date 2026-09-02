"""Nocturnal Luxury Jewelry Spree Archetype."""

from typing import Dict, Any, List
import random
from datetime import datetime, timezone


class NocturnalLuxuryArchetype:
    """Generates high-ticket luxury watch/jewelry purchases in the middle of the night (3AM)."""

    @staticmethod
    def generate_spree(card_id: str) -> List[Dict[str, Any]]:
        # Simulate 3:30 AM nocturnal timestamp
        now = datetime.now(timezone.utc)
        nocturnal_time = now.replace(hour=3, minute=30, second=15)

        return [
            {
                "card_id": card_id,
                "cardholder_id": f"USR_{card_id[-5:]}",
                "amount": 7850.00,
                "currency": "INR",
                "merchant_id": "M_ROLEX_BOUTIQUE_01",
                "merchant_name": "Luxury Timepieces International",
                "merchant_category": "LUXURY_JEWELRY",
                "entry_mode": "CNP",
                "card_type": "CREDIT",
                "card_network": "AMEX",
                "country_code": "US",
                "ip_address": f"194.26.29.{random.randint(10, 99)}",
                "device_fingerprint": f"DEV_TOR_EXIT_{random.randint(100, 999)}",
                "failed_pin_attempts_24h": 0,
                "fraud_archetype": "NOCTURNAL_LUXURY",
                "timestamp": nocturnal_time.isoformat()
            }
        ]
