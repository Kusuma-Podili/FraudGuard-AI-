"""Account Takeover (ATO) Electronics Burst Archetype."""

from typing import Dict, Any, List
import random
from datetime import datetime, timezone


class AccountTakeoverArchetype:
    """Generates high-value electronics purchases following credential update."""

    @staticmethod
    def generate_burst(card_id: str, count: int = 3) -> List[Dict[str, Any]]:
        burst = []
        merchants = [
            ("M_APPLE_01", "Apple Store Online", "ELECTRONICS", 1899.00),
            ("M_BESTBUY_02", "BestBuy Tech Hub", "ELECTRONICS", 1450.00),
            ("M_NEWEGG_03", "Newegg Hardware", "ELECTRONICS", 920.00),
        ]
        base_time = datetime.now(timezone.utc)

        for i in range(min(count, len(merchants))):
            m_id, m_name, cat, price = merchants[i]
            burst.append({
                "card_id": card_id,
                "cardholder_id": f"USR_{card_id[-5:]}",
                "amount": price + round(random.uniform(-50.0, 150.0), 2),
                "currency": "INR",
                "merchant_id": m_id,
                "merchant_name": m_name,
                "merchant_category": cat,
                "entry_mode": "CNP",
                "card_type": "CREDIT",
                "card_network": "VISA",
                "country_code": "US",
                "ip_address": f"104.28.14.{random.randint(10, 99)}",
                "device_fingerprint": f"DEV_TOR_BROWSER_{random.randint(100, 999)}",
                "failed_pin_attempts_24h": 0,
                "fraud_archetype": "ACCOUNT_TAKEOVER",
                "timestamp": base_time.isoformat()
            })
        return burst
