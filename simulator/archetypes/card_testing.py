"""Card Testing Probe Attack Archetype Generator.

Simulates fraud rings testing stolen card lists with sub-$3 authorizations
across varied merchant categories using rotating proxy IPs.
"""

from typing import Dict, Any, List
import random
from datetime import datetime, timezone


class CardTestingArchetype:
    """Generates bursts of low-dollar probe transactions."""

    @staticmethod
    def generate_wave(card_id: str, count: int = 6) -> List[Dict[str, Any]]:
        merchants = [
            ("M_STREAM_01", "Netflix Subscription", "DIGITAL_GOODS"),
            ("M_CHARITY_02", "Save Wildlife Fund", "NON_PROFIT"),
            ("M_GAS_03", "QuickStop Fuel", "GAS_STATION"),
            ("M_APP_04", "AppStore Micro-Pay", "DIGITAL_GOODS"),
        ]
        wave = []
        base_time = datetime.now(timezone.utc)

        for i in range(count):
            m_id, m_name, cat = random.choice(merchants)
            wave.append({
                "card_id": card_id,
                "cardholder_id": f"USR_{card_id[-5:]}",
                "amount": round(random.uniform(0.35, 2.50), 2),
                "currency": "USD",
                "merchant_id": m_id,
                "merchant_name": m_name,
                "merchant_category": cat,
                "entry_mode": "CNP",
                "card_type": "CREDIT",
                "card_network": "VISA",
                "country_code": "US",
                "ip_address": f"198.51.100.{random.randint(10, 250)}",
                "device_fingerprint": f"DEV_BOT_{random.randint(100, 999)}",
                "failed_pin_attempts_24h": 0,
                "fraud_archetype": "CARD_TESTING",
                "timestamp": base_time.isoformat()
            })
        return wave
