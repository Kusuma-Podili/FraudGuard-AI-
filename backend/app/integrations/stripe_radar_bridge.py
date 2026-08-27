"""Payment Gateway & Radar Ingestion Bridge (Stripe, Adyen, Checkout.com).

Harmonizes heterogeneous payment provider webhook payloads into unified
canonical transaction structures for FraudGuard AI sub-20ms scoring.
"""

from __future__ import annotations
import hmac
import hashlib
import json
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Any
from datetime import datetime, timezone


class PaymentGatewayHarmonizer:
    """Standardizes external PSP payloads (Stripe, Adyen, Braintree) into FraudGuard schema."""

    @staticmethod
    def verify_stripe_webhook_signature(payload_bytes: bytes, sig_header: str, webhook_secret: str, tolerance_seconds: int = 300) -> bool:
        """Verify Stripe webhook cryptographic HMAC-SHA256 signature."""
        try:
            pairs = dict(item.split("=") for item in sig_header.split(","))
            t = pairs.get("t")
            v1 = pairs.get("v1")

            if not t or not v1:
                return False

            now = int(datetime.now(timezone.utc).timestamp())
            if abs(now - int(t)) > tolerance_seconds:
                return False  # Replay attack expired

            signed_payload = f"{t}.".encode("utf-8") + payload_bytes
            expected_sig = hmac.new(webhook_secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
            return hmac.compare_digest(expected_sig, v1)
        except Exception:
            return False

    @classmethod
    def transform_stripe_charge(cls, stripe_event: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a Stripe charge.succeeded / payment_intent.created payload into canonical format."""
        obj = stripe_event.get("data", {}).get("object", {})
        billing = obj.get("billing_details", {})
        payment_method = obj.get("payment_method_details", {})
        card = payment_method.get("card", {})

        return {
            "card_id": f"STRIPE_{card.get('fingerprint', 'UNKNOWN_CARD')}",
            "cardholder_id": obj.get("customer", "GUEST_USER"),
            "amount": float(obj.get("amount", 0)) / 100.0,
            "currency": str(obj.get("currency", "USD")).upper(),
            "merchant_id": "M_STRIPE_ACCOUNT",
            "merchant_category": "GENERAL_RETAIL",
            "entry_mode": "CNP",
            "card_type": str(card.get("funding", "CREDIT")).upper(),
            "card_network": str(card.get("brand", "VISA")).upper(),
            "country_code": str(card.get("country", "US")).upper(),
            "ip_address": obj.get("outcome", {}).get("seller_message", "127.0.0.1"),
            "device_fingerprint": obj.get("id", "DEV_STRIPE_WEB"),
            "failed_pin_attempts_24h": 0,
            "external_risk_score": float(obj.get("outcome", {}).get("risk_score", 0)) / 100.0,
        }

    @classmethod
    def transform_adyen_notification(cls, adyen_item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert an Adyen standard notification item into canonical schema."""
        req = adyen_item.get("NotificationRequestItem", {})
        amt_data = req.get("amount", {})
        amt = float(amt_data.get("value", 0)) / 100.0

        return {
            "card_id": f"ADYEN_{req.get('pspReference', 'UNKNOWN')}",
            "cardholder_id": "ADYEN_CUSTOMER",
            "amount": amt,
            "currency": amt_data.get("currency", "EUR"),
            "merchant_id": req.get("merchantAccountCode", "M_ADYEN"),
            "merchant_category": "E_COMMERCE",
            "entry_mode": "CNP",
            "card_type": "CREDIT",
            "card_network": str(req.get("paymentMethod", "VISA")).upper(),
            "country_code": "US",
            "failed_pin_attempts_24h": 0,
        }
