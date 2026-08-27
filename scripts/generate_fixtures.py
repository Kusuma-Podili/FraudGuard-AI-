"""Generator for Enterprise Synthetic Datasets, Merchant Directories, and Rule Catalogs."""

import json
import csv
import os
import random
from datetime import datetime, timedelta, timezone

from ml_engine.data.dataset_generator import SyntheticTransactionGenerator

def generate_all_fixtures():
    os.makedirs("ml_engine/data/fixtures", exist_ok=True)
    os.makedirs("backend/app/db/fixtures", exist_ok=True)
    os.makedirs("simulator/fixtures", exist_ok=True)

    gen = SyntheticTransactionGenerator(seed=2026)
    base_time = datetime.now(timezone.utc) - timedelta(days=60)

    # 1. Generate 35,000 historical transactions CSV
    csv_path = "ml_engine/data/fixtures/historical_transactions_35k.csv"
    print(f"Generating {csv_path}...")
    fieldnames = [
        "transaction_id", "card_id", "cardholder_id", "amount", "currency",
        "merchant_id", "merchant_name", "merchant_category", "entry_mode",
        "card_type", "card_network", "latitude", "longitude", "country_code",
        "device_fingerprint", "ip_address", "is_fraud", "fraud_archetype",
        "timestamp"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(35000):
            t = base_time + timedelta(seconds=i * 140)
            is_fraud = random.random() < 0.02
            tx = gen.generate_single_transaction(timestamp=t, force_fraud=is_fraud)
            writer.writerow({
                "transaction_id": tx["transaction_id"],
                "card_id": tx["card_id"],
                "cardholder_id": tx["cardholder_id"],
                "amount": tx["amount"],
                "currency": tx.get("currency", "USD"),
                "merchant_id": tx["merchant_id"],
                "merchant_name": tx.get("merchant_name", tx["merchant_id"]),
                "merchant_category": tx["merchant_category"],
                "entry_mode": tx["entry_mode"],
                "card_type": tx["card_type"],
                "card_network": tx["card_network"],
                "latitude": tx.get("latitude", 37.7749),
                "longitude": tx.get("longitude", -122.4194),
                "country_code": tx["country_code"],
                "device_fingerprint": tx["device_fingerprint"],
                "ip_address": tx["ip_address"],
                "is_fraud": 1 if tx.get("is_fraud") else 0,
                "fraud_archetype": tx.get("fraud_archetype", "LEGITIMATE"),
                "timestamp": tx["timestamp"]
            })

    # 2. Generate Merchant Directory Catalog (5,000 merchants JSON)
    merchant_path = "backend/app/db/fixtures/merchants_catalog_5k.json"
    print(f"Generating {merchant_path}...")
    categories = ["GROCERY", "ELECTRONICS", "LUXURY_JEWELRY", "GAMBLING", "CRYPTO_EXCHANGE", "GAS_STATION", "TRAVEL_AIRLINE", "RESTAURANT", "DIGITAL_GOODS", "GENERAL_RETAIL"]
    merchants = []
    for i in range(5000):
        cat = random.choice(categories)
        is_risky = cat in ["CRYPTO_EXCHANGE", "GAMBLING", "LUXURY_JEWELRY"]
        risk_score = round(random.uniform(0.35, 0.95) if is_risky else random.uniform(0.01, 0.25), 4)
        merchants.append({
            "merchant_id": f"M_ENT_{i:05d}",
            "name": f"Global Merchant Store {i:05d}",
            "category": cat,
            "mcc_code": str(random.randint(3000, 8999)),
            "country_code": random.choice(["US", "GB", "DE", "FR", "JP", "CY", "SG", "AU"]),
            "historical_risk_score": risk_score,
            "chargeback_rate": round(risk_score * 0.08, 4),
            "is_blacklisted": bool(risk_score > 0.88),
        })
    with open(merchant_path, "w", encoding="utf-8") as fp:
        json.dump(merchants, fp, indent=2)

    # 3. Generate BIN Range Directory (3,000 BINs JSON)
    bin_path = "backend/app/db/fixtures/bin_ranges_3k.json"
    print(f"Generating {bin_path}...")
    bins = []
    networks = ["VISA", "MASTERCARD", "AMEX", "DISCOVER"]
    for i in range(3000):
        bin_num = f"{random.randint(400000, 699999)}"
        bins.append({
            "bin_prefix": bin_num,
            "issuer_bank": f"International Commercial Bank #{random.randint(1, 200)}",
            "card_network": random.choice(networks),
            "card_type": random.choice(["CREDIT", "DEBIT", "PREPAID"]),
            "country_iso": random.choice(["US", "CA", "GB", "DE", "FR", "JP", "IN", "BR"]),
            "is_prepaid_anonymous": bool(random.random() < 0.08),
        })
    with open(bin_path, "w", encoding="utf-8") as fp:
        json.dump(bins, fp, indent=2)

    print("All fixtures generated successfully!")

if __name__ == "__main__":
    generate_all_fixtures()
