"""Credential Stuffing / PIN Brute Force Archetype."""

from typing import Dict, Any, List
import random
from datetime import datetime, timezone


class CredentialStuffingArchetype:
    """Generates consecutive failed authorization attempts triggering security controls."""

    @staticmethod
    def generate_attack(card_id: str) -> List[Dict[str, Any]]:
        attempts = []
        base_time = datetime.now(timezone.utc)

        # 3 Failed attempts followed by a high-value withdrawal
        for failed_count in range(1, 4):
            attempts.append({
                "card_id": card_id,
                "cardholder_id": f"USR_{card_id[-5:]}",
                "amount": round(random.uniform(40.0, 100.0), 2),
                "currency": "INR",
                "merchant_id": "M_ATM_CHASE_04",
                "merchant_name": "ATM Cash Machine",
                "merchant_category": "ATM_WITHDRAWAL",
                "entry_mode": "CHIP",
                "card_type": "DEBIT",
                "card_network": "VISA",
                "country_code": "US",
                "failed_pin_attempts_24h": failed_count,
                "fraud_archetype": "CREDENTIAL_STUFFING",
                "timestamp": base_time.isoformat()
            })

        # The 4th attack attempt
        attempts.append({
            "card_id": card_id,
            "cardholder_id": f"USR_{card_id[-5:]}",
            "amount": 2500.00,
            "currency": "INR",
            "merchant_id": "M_ATM_CHASE_04",
            "merchant_name": "ATM Cash Machine",
            "merchant_category": "ATM_WITHDRAWAL",
            "entry_mode": "CHIP",
            "card_type": "DEBIT",
            "card_network": "VISA",
            "country_code": "US",
            "failed_pin_attempts_24h": 4,
            "fraud_archetype": "CREDENTIAL_STUFFING",
            "timestamp": base_time.isoformat()
        })
        return attempts
