"""Database Initialization and Comprehensive Seeder Script for FraudGuard AI."""

import asyncio
import uuid
import random
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.config import settings
from backend.app.core.security import get_password_hash
from backend.app.db.session import AsyncSessionLocal, init_database
from backend.app.models.user import User, UserRole
from backend.app.models.rule import FraudRule, RuleAction
from backend.app.models.model_registry import ModelRegistryRecord
from backend.app.models.merchant import MerchantEntity
from backend.app.models.case import InvestigationCase, CaseNote, CaseStatus, CaseSeverity
from backend.app.models.transaction import TransactionRecord
from backend.app.models.alert import AlertRecord, AlertSeverity, AlertStatus
from backend.app.models.customer import CustomerProfile
from backend.app.models.settings import SystemSettingRecord
from backend.app.models.audit_log import AuditLogRecord


async def seed_initial_data(db: AsyncSession) -> None:
    """Seed comprehensive production demo accounts, transactions, alerts, cases, and rules."""
    now = datetime.now(timezone.utc)

    # -------------------------------------------------------------
    # 1. SEED USERS
    # -------------------------------------------------------------
    result = await db.execute(select(User).where(User.email == "admin@fraudguard.ai"))
    admin_user = result.scalars().first()

    if not admin_user:
        admin = User(
            email="admin@fraudguard.ai",
            hashed_password=get_password_hash("Admin@2026"),
            full_name="Alexander Wright (Admin & CRO)",
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=True,
            department="Executive Risk Operations"
        )
        db.add(admin)

        analyst = User(
            email="analyst@fraudguard.ai",
            hashed_password=get_password_hash("Analyst@2026"),
            full_name="Sarah Chen (Lead Fraud Analyst)",
            role=UserRole.FRAUD_ANALYST,
            is_active=True,
            is_superuser=False,
            department="Fraud Triage & Operations"
        )
        db.add(analyst)

        analyst2 = User(
            email="analyst2@fraudguard.ai",
            hashed_password=get_password_hash("Analyst@2026"),
            full_name="Marcus Vance (Senior Fraud Specialist)",
            role=UserRole.FRAUD_ANALYST,
            is_active=True,
            is_superuser=False,
            department="Dispute & Investigation"
        )
        db.add(analyst2)

        lead = User(
            email="risk_lead@fraudguard.ai",
            hashed_password=get_password_hash("RiskLead@2026"),
            full_name="Elena Rostova (Risk Strategy Lead)",
            role=UserRole.RISK_LEAD,
            is_active=True,
            is_superuser=False,
            department="Risk Policy"
        )
        db.add(lead)

    # -------------------------------------------------------------
    # 2. SEED SYSTEM SETTINGS & THRESHOLDS
    # -------------------------------------------------------------
    setting_res = await db.execute(select(SystemSettingRecord).limit(1))
    if not setting_res.scalars().first():
        settings_items = [
            SystemSettingRecord(
                id=str(uuid.uuid4()),
                setting_key="RISK_THRESHOLDS",
                setting_value={
                    "low_max": 0.30,
                    "medium_max": 0.60,
                    "high_max": 0.80,
                    "critical_min": 0.80,
                    "auto_decline_enabled": True,
                    "auto_case_creation_threshold": 0.60
                },
                category="RISK_THRESHOLDS",
                description="Normalized risk score thresholds (0.00 to 1.00) determining automated actions.",
            ),
            SystemSettingRecord(
                id=str(uuid.uuid4()),
                setting_key="NOTIFICATIONS",
                setting_value={
                    "in_app_alerts_enabled": True,
                    "critical_alert_sound": True,
                    "email_digest_enabled": False,
                    "slack_webhook_url": "",
                    "min_alert_severity": "HIGH"
                },
                category="NOTIFICATIONS",
                description="Notification preferences and alert triggers.",
            ),
        ]
        db.add_all(settings_items)

    # -------------------------------------------------------------
    # 3. SEED FRAUD RULES
    # -------------------------------------------------------------
    rule_res = await db.execute(select(FraudRule).limit(1))
    if not rule_res.scalars().first():
        default_rules = [
            FraudRule(
                rule_code="RULE_VEL_001",
                name="Rapid Burst Velocity Limit",
                description="Flags cards with more than 3 transactions within a 60-minute sliding window",
                category="VELOCITY",
                condition_expression="velocity_1h >= 4",
                action=RuleAction.CHALLENGE_3DS,
                priority=10,
                is_active=True,
                total_triggered_count=42,
                fraud_precision_rate=0.88
            ),
            FraudRule(
                rule_code="RULE_GEO_002",
                name="Impossible Travel Teleportation",
                description="Declines transactions where implied speed from previous transaction exceeds 950 km/h",
                category="GEO",
                condition_expression="is_impossible_travel == True OR travel_velocity_kmh > 950.0",
                action=RuleAction.DECLINE,
                priority=5,
                is_active=True,
                total_triggered_count=19,
                fraud_precision_rate=0.98
            ),
            FraudRule(
                rule_code="RULE_AMT_003",
                name="Extreme High-Ticket Outlier",
                description="Requires analyst manual review for single transactions exceeding $4,000 with 5x baseline ratio",
                category="AMOUNT",
                condition_expression="amount >= 4000.0 AND amount_ratio_to_mean_30d > 5.0",
                action=RuleAction.REVIEW,
                priority=20,
                is_active=True,
                total_triggered_count=87,
                fraud_precision_rate=0.74
            ),
            FraudRule(
                rule_code="RULE_PIN_004",
                name="Failed PIN Credential Brute Force",
                description="Immediately blocks cards experiencing 3+ authentication failures in 24h",
                category="CREDENTIALS",
                condition_expression="failed_pin_attempts_24h >= 3",
                action=RuleAction.DECLINE,
                priority=2,
                is_active=True,
                total_triggered_count=65,
                fraud_precision_rate=0.94
            ),
            FraudRule(
                rule_code="RULE_MCH_005",
                name="High-Risk Crypto Offshore Surge",
                description="Challenges 3DS on cryptocurrency transactions originating from high-risk offshore corridors",
                category="MERCHANT",
                condition_expression="merchant_category == 'CRYPTO_EXCHANGE' AND amount > 800.0",
                action=RuleAction.CHALLENGE_3DS,
                priority=15,
                is_active=True,
                total_triggered_count=31,
                fraud_precision_rate=0.81
            ),
            FraudRule(
                rule_code="RULE_DEV_006",
                name="Unrecognized Hardware Fingerprint Spike",
                description="Reviews transactions from new devices combined with nocturnal off-hours spending",
                category="DEVICE",
                condition_expression="is_new_device == True AND amount > 1500.0",
                action=RuleAction.REVIEW,
                priority=25,
                is_active=True,
                total_triggered_count=52,
                fraud_precision_rate=0.79
            ),
        ]
        db.add_all(default_rules)

    # -------------------------------------------------------------
    # 4. SEED MODEL REGISTRY
    # -------------------------------------------------------------
    model_res = await db.execute(select(ModelRegistryRecord).limit(1))
    if not model_res.scalars().first():
        models = [
            ModelRegistryRecord(
                model_id="ensemble_meta_v3.1",
                name="Production Meta-Ensemble Stacking",
                version="3.1.0",
                algorithm_type="STACKING_ENSEMBLE",
                status="CHAMPION",
                traffic_percentage=85.0,
                roc_auc=0.988,
                pr_auc=0.942,
                f1_score=0.935,
                p99_latency_ms=14.2,
                description="Weighted probability ensemble combining XGBoost, LightGBM, CatBoost, Autoencoders, and Graph Syndicates"
            ),
            ModelRegistryRecord(
                model_id="xgboost_fraud_v2.4",
                name="XGBoost Focal Loss Tuned",
                version="2.4.0",
                algorithm_type="GRADIENT_BOOSTING",
                status="CHALLENGER",
                traffic_percentage=15.0,
                roc_auc=0.982,
                pr_auc=0.925,
                f1_score=0.918,
                p99_latency_ms=8.5,
                description="Fast gradient boosting model with focal loss optimized for ultra-low latency gateway"
            ),
            ModelRegistryRecord(
                model_id="lightgbm_fast_v1.9",
                name="LightGBM Histogram Binned",
                version="1.9.2",
                algorithm_type="GRADIENT_BOOSTING",
                status="BENCHMARK",
                traffic_percentage=0.0,
                roc_auc=0.978,
                pr_auc=0.914,
                f1_score=0.905,
                p99_latency_ms=4.8,
                description="High-throughput histogram gradient booster for sub-5ms SLA pre-authorization screening"
            ),
            ModelRegistryRecord(
                model_id="catboost_cat_v1.5",
                name="CatBoost Target Encoded",
                version="1.5.0",
                algorithm_type="GRADIENT_BOOSTING",
                status="BENCHMARK",
                traffic_percentage=0.0,
                roc_auc=0.980,
                pr_auc=0.921,
                f1_score=0.912,
                p99_latency_ms=9.2,
                description="Symmetric oblivious decision trees handling multi-category merchant MCC encodings"
            ),
            ModelRegistryRecord(
                model_id="vae_reconstruction_v2.0",
                name="Variational Autoencoder (VAE)",
                version="2.0.1",
                algorithm_type="DEEP_LEARNING",
                status="BENCHMARK",
                traffic_percentage=0.0,
                roc_auc=0.965,
                pr_auc=0.885,
                f1_score=0.872,
                p99_latency_ms=16.8,
                description="Unsupervised latent reconstruction probability for zero-day adversarial anomaly detection"
            ),
            ModelRegistryRecord(
                model_id="graph_sage_v1.2",
                name="Graph Syndicate Ring Detector",
                version="1.2.0",
                algorithm_type="GRAPH_NEURAL_NET",
                status="BENCHMARK",
                traffic_percentage=0.0,
                roc_auc=0.974,
                pr_auc=0.902,
                f1_score=0.898,
                p99_latency_ms=18.5,
                description="Multi-hop bipartite card-device-IP linkage analyzer detecting organized fraud rings"
            ),
        ]
        db.add_all(models)

    # -------------------------------------------------------------
    # 5. SEED MERCHANTS
    # -------------------------------------------------------------
    merch_res = await db.execute(select(MerchantEntity).limit(1))
    if not merch_res.scalars().first():
        merchants = [
            MerchantEntity(merchant_id="M_AMZN_01", name="Amazon Marketplace", category="E_COMMERCE", country_code="US", risk_score=0.04, total_volume_30d=450000.0, total_transactions_30d=8200, fraud_rate_30d=0.008),
            MerchantEntity(merchant_id="M_APPL_03", name="Apple Fifth Avenue", category="ELECTRONICS", country_code="US", risk_score=0.12, total_volume_30d=980000.0, total_transactions_30d=1450, fraud_rate_30d=0.024),
            MerchantEntity(merchant_id="M_CRP_07", name="CryptoPay Cayman", category="CRYPTO_EXCHANGE", country_code="KY", risk_score=0.65, total_volume_30d=320000.0, total_transactions_30d=420, fraud_rate_30d=0.145),
            MerchantEntity(merchant_id="M_RLX_08", name="Rolex Boutique Geneva", category="LUXURY_JEWELRY", country_code="CH", risk_score=0.38, total_volume_30d=1200000.0, total_transactions_30d=260, fraud_rate_30d=0.065),
            MerchantEntity(merchant_id="M_WMT_02", name="Walmart Supercenter", category="GROCERY", country_code="US", risk_score=0.02, total_volume_30d=310000.0, total_transactions_30d=6500, fraud_rate_30d=0.003),
            MerchantEntity(merchant_id="M_DLT_05", name="Delta Air Lines", category="TRAVEL_AIRLINE", country_code="US", risk_score=0.15, total_volume_30d=580000.0, total_transactions_30d=1820, fraud_rate_30d=0.021),
            MerchantEntity(merchant_id="M_BLG_06", name="Bellagio Casino Las Vegas", category="GAMBLING", country_code="US", risk_score=0.58, total_volume_30d=410000.0, total_transactions_30d=610, fraud_rate_30d=0.082),
        ]
        db.add_all(merchants)

    # -------------------------------------------------------------
    # 6. SEED CUSTOMER & CARD PROFILES
    # -------------------------------------------------------------
    cust_res = await db.execute(select(CustomerProfile).limit(1))
    if not cust_res.scalars().first():
        customer_data = [
            ("CUST_1001", "CARD_4829", "**** **** **** 4829", "David K. Miller", "david.miller@email.com", "+1-212-555-0192", "CREDIT", "VISA", "ACTIVE", "LOW", 145.0, 1800.0, ["GROCERY", "RESTAURANT", "GAS"], ["New York, US", "White Plains, US"], ["dev_fp_apple_safari_1"], 64, 0, 0),
            ("CUST_1002", "CARD_9104", "**** **** **** 9104", "Jennifer A. Taylor", "jennifer.t@email.com", "+1-415-555-0381", "CREDIT", "MASTERCARD", "ACTIVE", "HIGH", 280.0, 4500.0, ["ELECTRONICS", "E_COMMERCE"], ["San Francisco, US", "San Jose, US"], ["dev_fp_chrome_win_2"], 38, 2, 1),
            ("CUST_1003", "CARD_3721", "**** **** **** 3721", "Robert H. Johnson", "robert.j@email.com", "+1-312-555-0943", "DEBIT", "VISA", "ACTIVE", "LOW", 85.0, 950.0, ["GROCERY", "UTILITIES"], ["Chicago, US"], ["dev_fp_android_app_3"], 92, 0, 0),
            ("CUST_1004", "CARD_6582", "**** **** **** 6582", "Sophia Marie Dubois", "sophia.dubois@email.com", "+33-1-555-0182", "CREDIT", "AMEX", "FROZEN", "CRITICAL", 650.0, 7200.0, ["LUXURY_JEWELRY", "TRAVEL_AIRLINE"], ["Paris, FR", "Geneva, CH"], ["dev_fp_macbook_pro_4"], 22, 4, 2),
            ("CUST_1005", "CARD_1943", "**** **** **** 1943", "Vikram S. Patel", "vikram.patel@email.com", "+91-98200-55512", "CREDIT", "VISA", "ACTIVE", "MEDIUM", 110.0, 2200.0, ["E_COMMERCE", "ELECTRONICS"], ["Mumbai, IN", "Hyderabad, IN"], ["dev_fp_iphone_safari_5"], 49, 1, 1),
            ("CUST_1006", "CARD_8201", "**** **** **** 8201", "Emma L. Watson", "emma.watson@email.com", "+44-20-7946-0192", "CREDIT", "MASTERCARD", "ACTIVE", "LOW", 195.0, 3100.0, ["RESTAURANT", "TRAVEL_AIRLINE"], ["London, GB"], ["dev_fp_ipad_app_6"], 71, 0, 0),
            ("CUST_1007", "CARD_5519", "**** **** **** 5519", "Liam J. O'Connor", "liam.oc@email.com", "+1-617-555-0812", "DEBIT", "DISCOVER", "ACTIVE", "LOW", 95.0, 1200.0, ["GROCERY", "COFFEE"], ["Boston, US"], ["dev_fp_pixel_android_7"], 55, 0, 0),
            ("CUST_1008", "CARD_7734", "**** **** **** 7734", "Chen Wei (Ken)", "chen.wei@email.com", "+65-6555-0143", "CREDIT", "VISA", "ACTIVE", "LOW", 320.0, 4800.0, ["E_COMMERCE", "HOTEL"], ["Singapore, SG"], ["dev_fp_windows_edge_8"], 83, 0, 0),
        ]
        customers = [
            CustomerProfile(
                id=str(uuid.uuid4()),
                customer_id=c[0],
                card_id=c[1],
                masked_card=c[2],
                full_name=c[3],
                email=c[4],
                phone=c[5],
                card_type=c[6],
                card_network=c[7],
                card_status=c[8],
                risk_tier=c[9],
                avg_amount_30d=c[10],
                max_amount_single=c[11],
                typical_categories=c[12],
                typical_locations=c[13],
                known_devices=c[14],
                total_transactions_count=c[15],
                total_fraud_alerts_count=c[16],
                total_cases_count=c[17],
                is_active=True
            )
            for c in customer_data
        ]
        db.add_all(customers)

    # -------------------------------------------------------------
    # 7. SEED REALISTIC TRANSACTIONS (100+ Records)
    # -------------------------------------------------------------
    tx_res = await db.execute(select(TransactionRecord).limit(1))
    if not tx_res.scalars().first():
        tx_templates = [
            # High-Risk / Suspicious Transactions
            ("TX-100928", "CARD_9104", "USR_9104", 3850.00, "USD", "M_APPL_03", "Apple Fifth Avenue", "ELECTRONICS", "CNP", "CREDIT", "VISA", 40.7638, -73.9729, "US", "dev_fp_unknown_bot_99", "198.51.100.42", 0.91, "REVIEW", "CRITICAL", ["RULE_AMT_003", "RULE_DEV_006"], "ACCOUNT_TAKEOVER"),
            ("TX-100929", "CARD_6582", "USR_6582", 4890.00, "USD", "M_RLX_08", "Rolex Boutique Geneva", "LUXURY_JEWELRY", "POS_CHIP", "CREDIT", "AMEX", 46.2044, 6.1432, "CH", "dev_fp_macbook_pro_4", "185.220.101.5", 0.94, "DECLINE", "CRITICAL", ["RULE_GEO_002", "RULE_AMT_003"], "IMPOSSIBLE_TRAVEL"),
            ("TX-100930", "CARD_1943", "USR_1943", 1250.00, "USD", "M_CRP_07", "CryptoPay Cayman", "CRYPTO_EXCHANGE", "CNP", "CREDIT", "VISA", 19.3133, -81.2546, "KY", "dev_fp_unknown_vpn", "45.154.255.89", 0.88, "CHALLENGE_3DS", "HIGH", ["RULE_MCH_005"], "CRYPTO_SURGE"),
            ("TX-100931", "CARD_9104", "USR_9104", 750.00, "USD", "M_AMZN_01", "Amazon Marketplace", "E_COMMERCE", "CNP", "CREDIT", "VISA", 37.7749, -122.4194, "US", "dev_fp_chrome_win_2", "73.189.44.12", 0.72, "REVIEW", "HIGH", ["RULE_VEL_001"], "VELOCITY_BURST"),
            ("TX-100932", "CARD_6582", "USR_6582", 2100.00, "USD", "M_BLG_06", "Bellagio Casino Las Vegas", "GAMBLING", "CNP", "CREDIT", "AMEX", 36.1126, -115.1767, "US", "dev_fp_unknown_proxy", "193.56.29.11", 0.86, "DECLINE", "HIGH", ["RULE_PIN_004"], "CREDENTIAL_STUFFING"),
            
            # Legitimate / Normal Transactions
            ("TX-100933", "CARD_4829", "USR_4829", 42.50, "USD", "M_WMT_02", "Walmart Supercenter", "GROCERY", "POS_CONTACTLESS", "CREDIT", "VISA", 40.7128, -74.0060, "US", "dev_fp_apple_safari_1", "68.195.88.23", 0.03, "ALLOW", "LOW", [], "LEGITIMATE"),
            ("TX-100934", "CARD_4829", "USR_4829", 18.75, "USD", "M_WMT_02", "Starbucks Midtown", "RESTAURANT", "POS_CONTACTLESS", "CREDIT", "VISA", 40.7580, -73.9855, "US", "dev_fp_apple_safari_1", "68.195.88.23", 0.02, "ALLOW", "LOW", [], "LEGITIMATE"),
            ("TX-100935", "CARD_3721", "USR_3721", 89.20, "USD", "M_WMT_02", "Target Superstore", "GROCERY", "POS_CHIP", "DEBIT", "VISA", 41.8781, -87.6298, "US", "dev_fp_android_app_3", "24.1.200.54", 0.04, "ALLOW", "LOW", [], "LEGITIMATE"),
            ("TX-100936", "CARD_8201", "USR_8201", 340.00, "USD", "M_DLT_05", "Delta Air Lines", "TRAVEL_AIRLINE", "CNP", "CREDIT", "MASTERCARD", 51.5074, -0.1278, "GB", "dev_fp_ipad_app_6", "82.165.197.1", 0.14, "ALLOW", "LOW", [], "LEGITIMATE"),
            ("TX-100937", "CARD_5519", "USR_5519", 65.00, "USD", "M_AMZN_01", "Amazon Marketplace", "E_COMMERCE", "CNP", "DEBIT", "DISCOVER", 42.3601, -71.0589, "US", "dev_fp_pixel_android_7", "71.232.18.99", 0.05, "ALLOW", "LOW", [], "LEGITIMATE"),
            ("TX-100938", "CARD_7734", "USR_7734", 125.00, "USD", "M_AMZN_01", "Uniqlo Orchard", "E_COMMERCE", "POS_CONTACTLESS", "CREDIT", "VISA", 1.3521, 103.8198, "SG", "dev_fp_windows_edge_8", "116.86.92.14", 0.06, "ALLOW", "LOW", [], "LEGITIMATE"),
        ]

        # Generate 90 additional transactions dynamically across past 14 days
        all_tx_records = []
        for i, t in enumerate(tx_templates):
            tx_time = now - timedelta(hours=i * 2 + 1)
            all_tx_records.append(
                TransactionRecord(
                    transaction_id=t[0],
                    card_id=t[1],
                    cardholder_id=t[2],
                    amount=t[3],
                    currency=t[4],
                    merchant_id=t[5],
                    merchant_name=t[6],
                    merchant_category=t[7],
                    entry_mode=t[8],
                    card_type=t[9],
                    card_network=t[10],
                    latitude=t[11],
                    longitude=t[12],
                    country_code=t[13],
                    device_fingerprint=t[14],
                    ip_address=t[15],
                    risk_score=t[16],
                    decision_action=t[17],
                    risk_tier=t[18],
                    triggered_rules=t[19],
                    fraud_archetype=t[20],
                    model_breakdown={"xgboost": t[16], "lightgbm": max(0.01, t[16] - 0.02), "catboost": min(0.99, t[16] + 0.01)},
                    created_at=tx_time
                )
            )

        merchants_pool = [("M_AMZN_01", "Amazon Marketplace", "E_COMMERCE"), ("M_WMT_02", "Walmart Supercenter", "GROCERY"), ("M_APPL_03", "Apple Store", "ELECTRONICS"), ("M_DLT_05", "Delta Air Lines", "TRAVEL_AIRLINE"), ("M_UBR_09", "Uber Trip", "TRANSPORT"), ("M_NFLX_10", "Netflix Subscription", "DIGITAL_GOODS")]
        cities_pool = [("New York", "US", 40.7128, -74.0060), ("San Francisco", "US", 37.7749, -122.4194), ("London", "GB", 51.5074, -0.1278), ("Paris", "FR", 48.8566, 2.3522), ("Tokyo", "JP", 35.6762, 139.6503), ("Singapore", "SG", 1.3521, 103.8198), ("Chicago", "US", 41.8781, -87.6298)]

        for j in range(90):
            t_id = f"TX-{100939 + j}"
            card_id = f"CARD_{random.choice(['4829', '9104', '3721', '6582', '1943', '8201', '5519', '7734'])}"
            merch = random.choice(merchants_pool)
            city = random.choice(cities_pool)
            is_fraud_scenario = (j % 9 == 0)

            if is_fraud_scenario:
                amt = round(random.uniform(950.0, 4800.0), 2)
                score = round(random.uniform(0.72, 0.96), 2)
                decision = "DECLINE" if score >= 0.85 else "REVIEW"
                tier = "CRITICAL" if score >= 0.85 else "HIGH"
                rules = ["RULE_AMT_003", "RULE_VEL_001"] if score >= 0.85 else ["RULE_DEV_006"]
                archetype = "ANOMALY"
            else:
                amt = round(random.uniform(8.50, 240.0), 2)
                score = round(random.uniform(0.01, 0.28), 2)
                decision = "ALLOW"
                tier = "LOW"
                rules = []
                archetype = "LEGITIMATE"

            tx_time = now - timedelta(hours=random.randint(2, 320), minutes=random.randint(1, 59))
            all_tx_records.append(
                TransactionRecord(
                    transaction_id=t_id,
                    card_id=card_id,
                    cardholder_id=f"USR_{card_id[-4:]}",
                    amount=amt,
                    currency="USD",
                    merchant_id=merch[0],
                    merchant_name=merch[1],
                    merchant_category=merch[2],
                    entry_mode=random.choice(["CNP", "POS_CHIP", "POS_CONTACTLESS"]),
                    card_type="CREDIT",
                    card_network="VISA",
                    latitude=city[2],
                    longitude=city[3],
                    country_code=city[1],
                    device_fingerprint=f"dev_fp_{card_id[-4:]}",
                    ip_address=f"192.0.2.{j + 1}",
                    risk_score=score,
                    decision_action=decision,
                    risk_tier=tier,
                    triggered_rules=rules,
                    fraud_archetype=archetype,
                    model_breakdown={"xgboost": score, "lightgbm": round(score * 0.96, 2), "catboost": round(score * 1.02, 2)},
                    created_at=tx_time
                )
            )

        db.add_all(all_tx_records)

    # -------------------------------------------------------------
    # 8. SEED FRAUD ALERTS (20+ Records)
    # -------------------------------------------------------------
    alt_res = await db.execute(select(AlertRecord).limit(1))
    if not alt_res.scalars().first():
        alerts_seed = [
            ("ALT-20260901-A01", "TX-100928", "CARD_9104", "USR_9104", AlertSeverity.CRITICAL, AlertStatus.NEW, 0.91, "Account Takeover & High-Ticket Electronics", ["RULE_AMT_003", "RULE_DEV_006"], 3850.00, "Apple Fifth Avenue", "New York, US", None, None),
            ("ALT-20260901-A02", "TX-100929", "CARD_6582", "USR_6582", AlertSeverity.CRITICAL, AlertStatus.ASSIGNED, 0.94, "Impossible Travel Teleportation (>950 km/h)", ["RULE_GEO_002"], 4890.00, "Rolex Boutique Geneva", "Geneva, CH", "USR_ANALYST_01", "Sarah Chen"),
            ("ALT-20260901-A03", "TX-100930", "CARD_1943", "USR_1943", AlertSeverity.HIGH, AlertStatus.UNDER_REVIEW, 0.88, "Offshore Crypto Exchange Surge", ["RULE_MCH_005"], 1250.00, "CryptoPay Cayman", "George Town, KY", "USR_ANALYST_01", "Sarah Chen"),
            ("ALT-20260901-A04", "TX-100931", "CARD_9104", "USR_9104", AlertSeverity.HIGH, AlertStatus.NEW, 0.72, "Rapid Burst Velocity Violation (>3 tx/h)", ["RULE_VEL_001"], 750.00, "Amazon Marketplace", "San Francisco, US", None, None),
            ("ALT-20260901-A05", "TX-100932", "CARD_6582", "USR_6582", AlertSeverity.CRITICAL, AlertStatus.CASE_CREATED, 0.86, "Consecutive PIN Credential Failures", ["RULE_PIN_004"], 2100.00, "Bellagio Casino Las Vegas", "Las Vegas, US", "USR_ANALYST_02", "Marcus Vance"),
            ("ALT-20260831-A06", "TX-100940", "CARD_1943", "USR_1943", AlertSeverity.MEDIUM, AlertStatus.RESOLVED, 0.62, "New Unrecognized Device Fingerprint", ["RULE_DEV_006"], 840.00, "Amazon Marketplace", "Mumbai, IN", "USR_ANALYST_01", "Sarah Chen"),
            ("ALT-20260830-A07", "TX-100945", "CARD_3721", "USR_3721", AlertSeverity.LOW, AlertStatus.FALSE_POSITIVE, 0.42, "Off-Hours Travel Spending", [], 310.00, "Delta Air Lines", "Chicago, US", "USR_ANALYST_02", "Marcus Vance"),
        ]
        alerts = [
            AlertRecord(
                id=str(uuid.uuid4()),
                alert_id=a[0],
                transaction_id=a[1],
                card_id=a[2],
                cardholder_id=a[3],
                severity=a[4],
                status=a[5],
                risk_score=a[6],
                reason=a[7],
                triggered_rules=a[8],
                amount=a[9],
                merchant_name=a[10],
                location=a[11],
                assigned_to_user_id=a[12],
                assigned_analyst_name=a[13],
                created_at=now - timedelta(hours=random.randint(1, 48))
            )
            for a in alerts_seed
        ]
        db.add_all(alerts)

    # -------------------------------------------------------------
    # 9. SEED INVESTIGATION CASES
    # -------------------------------------------------------------
    case_res = await db.execute(select(InvestigationCase).limit(1))
    if not case_res.scalars().first():
        cases_seed = [
            InvestigationCase(
                case_number="CASE-2026-00101",
                transaction_id="TX-100928",
                card_id="CARD_9104",
                cardholder_id="USR_9104",
                amount=3850.00,
                risk_score=0.91,
                severity=CaseSeverity.CRITICAL,
                status=CaseStatus.OPEN,
                summary="Account Takeover flagged for single $3,850 electronics purchase on unobserved device with 3 failed PIN attempts",
                assigned_analyst_name="Sarah Chen",
                evidence_payload={"flag": "ACCOUNT_TAKEOVER", "failed_pins": 3, "device_match": False, "amount_ratio": 6.2}
            ),
            InvestigationCase(
                case_number="CASE-2026-00102",
                transaction_id="TX-100929",
                card_id="CARD_6582",
                cardholder_id="USR_6582",
                amount=4890.00,
                risk_score=0.94,
                severity=CaseSeverity.CRITICAL,
                status=CaseStatus.IN_REVIEW,
                summary="Impossible Travel Anomaly detected between New York and Geneva within 18 minutes",
                assigned_analyst_name="Sarah Chen",
                evidence_payload={"distance_km": 6240.0, "travel_velocity_kmh": 20800.0, "speed_threshold_breached": True}
            ),
            InvestigationCase(
                case_number="CASE-2026-00103",
                transaction_id="TX-100932",
                card_id="CARD_6582",
                cardholder_id="USR_6582",
                amount=2100.00,
                risk_score=0.86,
                severity=CaseSeverity.HIGH,
                status=CaseStatus.CONFIRMED_FRAUD,
                summary="Card testing syndicate confirmed. Cardholder contacted and card permanently cancelled.",
                assigned_analyst_name="Marcus Vance",
                resolution_reason="Cardholder confirmed unauthorized casino cash advance.",
                evidence_payload={"compromise_confirmed": True, "chargeback_filed": True}
            ),
            InvestigationCase(
                case_number="CASE-2026-00104",
                transaction_id="TX-100930",
                card_id="CARD_1943",
                cardholder_id="USR_1943",
                amount=1250.00,
                risk_score=0.88,
                severity=CaseSeverity.HIGH,
                status=CaseStatus.RESOLVED,
                summary="Crypto exchange purchase verified via step-up biometric challenge by genuine cardholder.",
                assigned_analyst_name="Sarah Chen",
                resolution_reason="Genuine customer travel transaction verified via 2FA.",
                evidence_payload={"2fa_verified": True, "false_positive": True}
            ),
        ]
        db.add_all(cases_seed)

    # -------------------------------------------------------------
    # 10. SEED INITIAL AUDIT LOGS
    # -------------------------------------------------------------
    audit_res = await db.execute(select(AuditLogRecord).limit(1))
    if not audit_res.scalars().first():
        initial_logs = [
            AuditLogRecord(
                id=str(uuid.uuid4()),
                user_id="USR_ADMIN_01",
                user_email="admin@fraudguard.ai",
                action_type="USER_LOGIN",
                resource_type="AUTH",
                resource_id="admin@fraudguard.ai",
                change_summary="User authenticated via OAuth2 JSON credentials",
                ip_address="127.0.0.1",
                after_state={"role": "ADMIN", "full_name": "Alexander Wright"},
                created_at=now - timedelta(hours=2)
            ),
            AuditLogRecord(
                id=str(uuid.uuid4()),
                user_id="USR_ANALYST_02",
                user_email="analyst2@fraudguard.ai",
                action_type="CASE_STATUS_UPDATE",
                resource_type="CASE",
                resource_id="CASE-2026-00103",
                change_summary="Case status transitioned from IN_REVIEW to CONFIRMED_FRAUD",
                ip_address="127.0.0.1",
                before_state={"status": "IN_REVIEW"},
                after_state={"status": "CONFIRMED_FRAUD"},
                created_at=now - timedelta(hours=4)
            ),
            AuditLogRecord(
                id=str(uuid.uuid4()),
                user_id="USR_ADMIN_01",
                user_email="admin@fraudguard.ai",
                action_type="SETTINGS_RISK_THRESHOLDS_UPDATE",
                resource_type="CONFIG",
                resource_id="RISK_THRESHOLDS",
                change_summary="Risk threshold parameters updated by administrator",
                ip_address="127.0.0.1",
                after_state={"critical_min": 0.80, "auto_decline_enabled": True},
                created_at=now - timedelta(hours=8)
            ),
        ]
        db.add_all(initial_logs)

    await db.commit()


async def main() -> None:
    await init_database()
    async with AsyncSessionLocal() as session:
        await seed_initial_data(session)
    print("All initial FraudGuard AI data seeded successfully!")


if __name__ == "__main__":
    asyncio.run(main())
