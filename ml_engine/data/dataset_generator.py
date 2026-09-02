"""Realistic Financial Transaction Dataset Generator with Calibrated Fraud Attack Injections.

Synthesizes high-fidelity credit card transaction streams modeling:
- Cardholder personas with diurnal spending patterns and geographic anchors
- Merchant category codes (MCC) with empirical risk distributions
- 6 Advanced Fraud Attack Archetypes:
  1. Card Testing Attack (rapid micro-authorizations to test validity)
  2. Account Takeover (ATO) with sudden high-ticket electronics purchases
  3. Impossible Travel Anomaly (cross-continental POS swipes within minutes)
  4. High-Risk Crypto & Offshore Velocity Surge
  5. Credential Stuffing / Failed PIN Brute Force
  6. Nocturnal Luxury Goods Burst
"""

from __future__ import annotations
import math
import random
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple, Optional
import numpy as np


class SyntheticTransactionGenerator:
    """Generates synthetic financial credit card datasets with ground-truth fraud labels."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        random.seed(seed)

        self._merchants = self._init_merchants()
        self._cardholders = self._init_cardholders(n_cardholders=500)

    def _init_merchants(self) -> List[Dict[str, Any]]:
        """Define realistic merchant profiles with geographic coordinates and risk baselines."""
        return [
            {"id": "M_AMZN_01", "name": "Amazon Online Marketplace", "category": "E_COMMERCE", "lat": 47.6062, "lon": -122.3321, "country": "US", "risk": 0.04, "mean_amt": 55.0, "std_amt": 35.0},
            {"id": "M_WMT_02", "name": "Walmart Supercenter", "category": "GROCERY", "lat": 36.3729, "lon": -94.2088, "country": "US", "risk": 0.02, "mean_amt": 78.0, "std_amt": 45.0},
            {"id": "M_APPL_03", "name": "Apple Flagship Store", "category": "ELECTRONICS", "lat": 40.7638, "lon": -73.9729, "country": "US", "risk": 0.12, "mean_amt": 850.0, "std_amt": 600.0},
            {"id": "M_SHL_04", "name": "Shell Gas & Convenience", "category": "GAS_STATION", "lat": 29.7604, "lon": -95.3698, "country": "US", "risk": 0.08, "mean_amt": 45.0, "std_amt": 15.0},
            {"id": "M_DLT_05", "name": "Delta Air Lines", "category": "TRAVEL_AIRLINE", "lat": 33.7490, "lon": -84.3880, "country": "US", "risk": 0.10, "mean_amt": 420.0, "std_amt": 220.0},
            {"id": "M_BLG_06", "name": "Bellagio Hotel & Casino", "category": "GAMBLING", "lat": 36.1126, "lon": -115.1767, "country": "US", "risk": 0.45, "mean_amt": 650.0, "std_amt": 500.0},
            {"id": "M_CRP_07", "name": "CryptoPay Gateway", "category": "CRYPTO_EXCHANGE", "lat": 19.3133, "lon": -81.2546, "country": "KY", "risk": 0.65, "mean_amt": 1200.0, "std_amt": 950.0},
            {"id": "M_RLX_08", "name": "Rolex Boutique Geneva", "category": "LUXURY_JEWELRY", "lat": 46.2044, "lon": 6.1432, "country": "CH", "risk": 0.38, "mean_amt": 4800.0, "std_amt": 2500.0},
            {"id": "M_MCD_09", "name": "McDonald's Fast Food", "category": "RESTAURANT", "lat": 41.8781, "lon": -87.6298, "country": "US", "risk": 0.01, "mean_amt": 14.50, "std_amt": 6.0},
            {"id": "M_STM_10", "name": "Steam Digital Gaming", "category": "DIGITAL_GOODS", "lat": 47.6101, "lon": -122.2015, "country": "US", "risk": 0.15, "mean_amt": 35.0, "std_amt": 25.0},
        ]

    def _init_cardholders(self, n_cardholders: int) -> List[Dict[str, Any]]:
        """Generate diverse cardholder demographics, home locations, and spending habits."""
        us_cities = [
            ("New York", 40.7128, -74.0060, "US"),
            ("Los Angeles", 34.0522, -118.2437, "US"),
            ("Chicago", 41.8781, -87.6298, "US"),
            ("Houston", 29.7604, -95.3698, "US"),
            ("Phoenix", 33.4484, -112.0740, "US"),
            ("San Francisco", 37.7749, -122.4194, "US"),
            ("Seattle", 47.6062, -122.3321, "US"),
            ("Miami", 25.7617, -80.1918, "US"),
        ]

        cardholders = []
        card_types = ["CREDIT_STANDARD", "CREDIT_PLATINUM", "CREDIT_INFINITE", "DEBIT_STANDARD", "DEBIT_PREPAID"]
        networks = ["VISA", "MASTERCARD", "AMEX", "DISCOVER"]

        for i in range(n_cardholders):
            city, lat, lon, country = us_cities[i % len(us_cities)]
            # Add slight jitter to home coordinates (within ~15km)
            jitter_lat = lat + self.rng.normal(0, 0.05)
            jitter_lon = lon + self.rng.normal(0, 0.05)

            card_id = f"CARD_{100000 + i:06d}"
            cardholder_id = f"USR_{50000 + i:05d}"
            age = int(self.rng.integers(21, 75))
            monthly_income = float(self.rng.normal(5500, 2000))
            avg_tx_amount = float(max(15.0, self.rng.normal(65, 30)))

            cardholders.append({
                "card_id": card_id,
                "cardholder_id": cardholder_id,
                "age": age,
                "monthly_income": round(max(2000.0, monthly_income), 2),
                "home_lat": round(jitter_lat, 4),
                "home_lon": round(jitter_lon, 4),
                "home_city": city,
                "home_country": country,
                "card_type": random.choice(card_types),
                "card_network": random.choice(networks),
                "avg_30d_amount": round(avg_tx_amount, 2),
                "primary_device": f"DEV_{uuid.uuid4().hex[:8].upper()}",
                "primary_ip": f"192.168.{self.rng.integers(1, 254)}.{self.rng.integers(1, 254)}"
            })

        return cardholders

    def _diurnal_probability(self, hour: float) -> float:
        """Empirical probability density of card transactions by hour of day (0-24)."""
        # Bimodal Gaussian mixture model: morning peak ~13:00, evening peak ~19:30
        peak1 = math.exp(-0.5 * ((hour - 13.0) / 3.0) ** 2)
        peak2 = 0.8 * math.exp(-0.5 * ((hour - 19.5) / 2.5) ** 2)
        baseline = 0.08
        return (peak1 + peak2 + baseline) / 2.5

    def generate_single_transaction(
        self,
        timestamp: datetime,
        force_fraud: bool = False,
        fraud_archetype: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a single realistic transaction."""
        cardholder = random.choice(self._cardholders)
        merchant = random.choice(self._merchants)

        is_fraud = 1 if force_fraud else 0
        fraud_scenario = "LEGITIMATE"

        if force_fraud:
            archetypes = [
                "CARD_TESTING", "ACCOUNT_TAKEOVER", "IMPOSSIBLE_TRAVEL",
                "CRYPTO_VELOCITY", "CREDENTIAL_STUFFING", "NOCTURNAL_LUXURY"
            ]
            archetype = fraud_archetype or random.choice(archetypes)
            fraud_scenario = archetype

            if archetype == "CARD_TESTING":
                # Micro authorization probe (₹0.25 - ₹2.50) from unusual IP
                amount = round(float(self.rng.uniform(0.25, 2.50)), 2)
                entry_mode = "CNP"
                merchant = next((m for m in self._merchants if m["category"] == "DIGITAL_GOODS"), merchant)
                failed_pins = int(self.rng.integers(0, 3))
                lat = cardholder["home_lat"] + self.rng.normal(0, 0.5)
                lon = cardholder["home_lon"] + self.rng.normal(0, 0.5)
                country = "US"

            elif archetype == "ACCOUNT_TAKEOVER":
                # Sudden massive ticket electronics purchase with new device
                amount = round(float(self.rng.uniform(1800.0, 4500.0)), 2)
                entry_mode = "E_COMMERCE"
                merchant = next((m for m in self._merchants if m["category"] == "ELECTRONICS"), merchant)
                failed_pins = int(self.rng.integers(1, 4))
                lat = cardholder["home_lat"] + self.rng.normal(0, 2.0)
                lon = cardholder["home_lon"] + self.rng.normal(0, 2.0)
                country = "US"

            elif archetype == "IMPOSSIBLE_TRAVEL":
                # Transaction in foreign country far from cardholder home
                amount = round(float(self.rng.uniform(250.0, 1500.0)), 2)
                entry_mode = "SWIPE"
                lat, lon, country = 48.8566, 2.3522, "FR"  # Paris
                failed_pins = 0

            elif archetype == "CRYPTO_VELOCITY":
                # High risk crypto offshore cash out
                amount = round(float(self.rng.uniform(900.0, 5000.0)), 2)
                entry_mode = "CNP"
                merchant = next((m for m in self._merchants if m["category"] == "CRYPTO_EXCHANGE"), merchant)
                lat, lon, country = merchant["lat"], merchant["lon"], merchant["country"]
                failed_pins = 1

            elif archetype == "CREDENTIAL_STUFFING":
                # Multiple failed PIN attempts
                amount = round(float(self.rng.uniform(100.0, 800.0)), 2)
                entry_mode = "MANUAL_KEYED"
                failed_pins = int(self.rng.integers(3, 7))
                lat = cardholder["home_lat"] + self.rng.normal(0, 0.1)
                lon = cardholder["home_lon"] + self.rng.normal(0, 0.1)
                country = cardholder["home_country"]

            else:  # NOCTURNAL_LUXURY
                amount = round(float(self.rng.uniform(3000.0, 9500.0)), 2)
                entry_mode = "CNP"
                merchant = next((m for m in self._merchants if m["category"] == "LUXURY_JEWELRY"), merchant)
                failed_pins = 0
                lat = cardholder["home_lat"] + self.rng.normal(0, 0.2)
                lon = cardholder["home_lon"] + self.rng.normal(0, 0.2)
                country = cardholder["home_country"]

        else:
            # Normal Legitimate Distribution
            entry_modes = ["CHIP", "CONTACTLESS", "E_COMMERCE", "CNP"]
            entry_mode = random.choice(entry_modes)
            failed_pins = 0 if self.rng.random() > 0.03 else 1
            # Normal amount around merchant baseline
            base_amt = self.rng.normal(merchant["mean_amt"], merchant["std_amt"])
            amount = round(max(1.50, float(base_amt)), 2)
            # Local vicinity (within 25km)
            lat = cardholder["home_lat"] + float(self.rng.normal(0, 0.08))
            lon = cardholder["home_lon"] + float(self.rng.normal(0, 0.08))
            country = cardholder["home_country"]

        tx_id = f"TX_{uuid.uuid4().hex[:12].upper()}"

        return {
            "transaction_id": tx_id,
            "card_id": cardholder["card_id"],
            "cardholder_id": cardholder["cardholder_id"],
            "amount": amount,
            "currency": "INR",
            "merchant_id": merchant["id"],
            "merchant_name": merchant["name"],
            "merchant_category": merchant["category"],
            "entry_mode": entry_mode,
            "card_type": cardholder["card_type"],
            "card_network": cardholder["card_network"],
            "cardholder_age": cardholder["age"],
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "country_code": country,
            "device_type": "MOBILE_APP" if entry_mode == "E_COMMERCE" else "POS_TERMINAL",
            "device_fingerprint": cardholder["primary_device"] if not force_fraud else f"DEV_{uuid.uuid4().hex[:8].upper()}",
            "ip_address": cardholder["primary_ip"] if not force_fraud else f"10.0.{self.rng.integers(1, 254)}.{self.rng.integers(1, 254)}",
            "failed_pin_attempts_24h": failed_pins,
            "timestamp": timestamp.isoformat(),
            "is_fraud": is_fraud,
            "fraud_archetype": fraud_scenario,
        }

    def generate_dataset(
        self,
        n_samples: int = 10000,
        fraud_ratio: float = 0.03,
        start_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Generate a chronologically ordered dataset of transactions with ground truth labels."""
        if start_time is None:
            start_time = datetime.now(timezone.utc) - timedelta(days=14)

        transactions: List[Dict[str, Any]] = []
        current_time = start_time
        target_fraud_count = int(n_samples * fraud_ratio)
        target_legit_count = n_samples - target_fraud_count

        fraud_indices = set(self.rng.choice(n_samples, size=target_fraud_count, replace=False))

        for i in range(n_samples):
            # Advance time by Poisson arrival process (mean interval 60 seconds adjusted by diurnal factor)
            hour_float = current_time.hour + current_time.minute / 60.0
            diurnal_weight = self._diurnal_probability(hour_float)
            interval_seconds = max(5.0, float(self.rng.exponential(scale=60.0 / diurnal_weight)))
            current_time += timedelta(seconds=interval_seconds)

            is_fraud_sample = (i in fraud_indices)
            tx = self.generate_single_transaction(timestamp=current_time, force_fraud=is_fraud_sample)
            transactions.append(tx)

        return transactions


def generate_fraud_dataset(n_samples: int = 5000, fraud_ratio: float = 0.03) -> List[Dict[str, Any]]:
    """Helper function to quickly generate a balanced synthetic evaluation dataset."""
    generator = SyntheticTransactionGenerator(seed=42)
    return generator.generate_dataset(n_samples=n_samples, fraud_ratio=fraud_ratio)
