"""Database Initialization and Seeder Script."""

import asyncio
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
from backend.app.models.case import InvestigationCase, CaseStatus, CaseSeverity
from backend.app.models.transaction import TransactionRecord


async def seed_initial_data(db: AsyncSession) -> None:
    """Seed initial demo accounts, default rules, and active models."""
    # 1. Seed Users
    result = await db.execute(select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL))
    admin_user = result.scalars().first()

    if not admin_user:
        admin = User(
            email=settings.FIRST_SUPERUSER_EMAIL,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            full_name="Chief Risk Officer (Admin)",
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
            department="Fraud Triage"
        )
        db.add(analyst)

        lead = User(
            email="risk_lead@fraudguard.ai",
            hashed_password=get_password_hash("RiskLead@2026"),
            full_name="Marcus Vance (Risk Strategy Lead)",
            role=UserRole.RISK_LEAD,
            is_active=True,
            is_superuser=False,
            department="Risk Policy"
        )
        db.add(lead)

    # 2. Seed Default Fraud Rules
    rule_res = await db.execute(select(FraudRule).limit(1))
    if not rule_res.scalars().first():
        default_rules = [
            FraudRule(
                rule_code="RULE_VEL_001",
                name="Rapid Burst Velocity Limit",
                description="Flags cards with more than 3 transactions within a 60-minute window",
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
                description="Requires analyst manual review for single transactions exceeding $4,000",
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
        ]
        db.add_all(default_rules)

    # 3. Seed Model Registry
    model_res = await db.execute(select(ModelRegistryRecord).limit(1))
    if not model_res.scalars().first():
        models = [
            ModelRegistryRecord(
                model_id="ensemble_meta_v3.1",
                name="Production Meta-Ensemble Stacking",
                version="3.1.0",
                algorithm_type="STACKING_ENSEMBLE",
                status="CHAMPION",
                traffic_percentage=90.0,
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
                traffic_percentage=10.0,
                roc_auc=0.982,
                pr_auc=0.925,
                f1_score=0.918,
                p99_latency_ms=8.5,
                description="Fast gradient boosting model with focal loss optimized for ultra-low latency gateway"
            ),
        ]
        db.add_all(models)

    # 4. Seed Sample Merchants
    merch_res = await db.execute(select(MerchantEntity).limit(1))
    if not merch_res.scalars().first():
        merchants = [
            MerchantEntity(merchant_id="M_AMZN_01", name="Amazon Marketplace", category="E_COMMERCE", country_code="US", risk_score=0.04, total_volume_30d=450000.0, total_transactions_30d=8200, fraud_rate_30d=0.008),
            MerchantEntity(merchant_id="M_APPL_03", name="Apple Fifth Avenue", category="ELECTRONICS", country_code="US", risk_score=0.12, total_volume_30d=980000.0, total_transactions_30d=1450, fraud_rate_30d=0.024),
            MerchantEntity(merchant_id="M_CRP_07", name="CryptoPay Cayman", category="CRYPTO_EXCHANGE", country_code="KY", risk_score=0.65, total_volume_30d=320000.0, total_transactions_30d=420, fraud_rate_30d=0.145),
            MerchantEntity(merchant_id="M_RLX_08", name="Rolex Boutique Geneva", category="LUXURY_JEWELRY", country_code="CH", risk_score=0.38, total_volume_30d=1200000.0, total_transactions_30d=260, fraud_rate_30d=0.065),
            MerchantEntity(merchant_id="M_WMT_02", name="Walmart Supercenter", category="GROCERY", country_code="US", risk_score=0.02, total_volume_30d=310000.0, total_transactions_30d=6500, fraud_rate_30d=0.003),
        ]
        db.add_all(merchants)

    # 5. Seed Initial Sample Investigation Cases
    case_res = await db.execute(select(InvestigationCase).limit(1))
    if not case_res.scalars().first():
        sample_cases = [
            InvestigationCase(
                case_number="CASE-2026-00101",
                transaction_id="TX_DEMO_001",
                card_id="CARD_100042",
                cardholder_id="USR_50042",
                amount=3850.00,
                risk_score=0.92,
                severity=CaseSeverity.CRITICAL,
                status=CaseStatus.OPEN,
                summary="High-ticket electronics transaction flagged for Account Takeover and failed PIN attempts",
                assigned_analyst_name="Sarah Chen",
                evidence_payload={"flag": "ACCOUNT_TAKEOVER", "failed_pins": 3, "device_match": False}
            ),
            InvestigationCase(
                case_number="CASE-2026-00102",
                transaction_id="TX_DEMO_002",
                card_id="CARD_100088",
                cardholder_id="USR_50088",
                amount=1420.00,
                risk_score=0.88,
                severity=CaseSeverity.HIGH,
                status=CaseStatus.IN_REVIEW,
                summary="Impossible Travel Anomaly detected between New York and Paris within 18 minutes",
                assigned_analyst_name="Sarah Chen",
                evidence_payload={"distance_km": 5840.0, "travel_velocity_kmh": 19460.0}
            ),
        ]
        db.add_all(sample_cases)

    await db.commit()


async def main() -> None:
    await init_database()
    async with AsyncSessionLocal() as session:
        await seed_initial_data(session)


if __name__ == "__main__":
    asyncio.run(main())
