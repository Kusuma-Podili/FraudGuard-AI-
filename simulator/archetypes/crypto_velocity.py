"""Offshore Crypto Velocity Cashout Archetype."""

from typing import Dict, Any, List
import random
from datetime import datetime, timezone


class CryptoVelocityArchetype:
    """Generates sequential rapid crypto deposit transactions."""

    @staticmethod
    def generate_surge(card_id: str, count: int = 4) -> List[Dict[str, Any]]:
        surge = []
        base_time = datetime.now(timezone.utc)

        for i in range(count):
            surge.append({
                "card_id": card_id,
                "cardholder_id": f"USR_{card_id[-5:]}",
                "amount": round(random.uniform(980.0, 4800.0), 2),
                "currency": "USD",
                "merchant_id": "M_BINANCE_OFFSHORE_01",
                "merchant_name": "Offshore Crypto Exchange",
                "merchant_category": "CRYPTO_EXCHANGE",
                "entry_mode": "CNP",
                "card_type": "DEBIT",
                "card_network": "MASTERCARD",
                "country_code": "CY",  # Cyprus / Offshore
                "ip_address": f"185.220.101.{random.randint(10, 200)}",
                "device_fingerprint": f"DEV_VPN_NODE_{random.randint(10, 99)}",
                "failed_pin_attempts_24h": 0,
                "fraud_archetype": "CRYPTO_VELOCITY",
                "timestamp": base_time.isoformat()
            })
        return surge
