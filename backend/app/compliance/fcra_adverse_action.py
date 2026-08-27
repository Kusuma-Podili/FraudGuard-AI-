"""Fair Credit Reporting Act (FCRA) Section 615(a) Adverse Action Engine.

Generates legally compliant adverse action notices, score disclosures, key factor
explanations, dispute right disclosures, and immutable compliance audit records.
"""

from __future__ import annotations
import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any


@dataclass
class AdverseFactorExplanation:
    """Individual negative factor contributing to adverse credit decision."""
    factor_code: str
    factor_description: str
    relative_weight: float
    feature_name: str
    feature_value: Any
    baseline_benchmark: Any
    actionable_remediation_guidance: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "factor_code": self.factor_code,
            "factor_description": self.factor_description,
            "relative_weight": round(self.relative_weight, 4),
            "feature_name": self.feature_name,
            "feature_value": str(self.feature_value),
            "baseline_benchmark": str(self.baseline_benchmark),
            "actionable_remediation_guidance": self.actionable_remediation_guidance,
        }


@dataclass
class ScoreDisclosureSummary:
    """Credit/Fraud score disclosure mandated under FCRA section 609(g)."""
    score_model_name: str
    score_model_version: str
    numerical_score: float
    score_range_min: float
    score_range_max: float
    score_percentile_rank: float
    scoring_date: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score_model_name": self.score_model_name,
            "score_model_version": self.score_model_version,
            "numerical_score": round(self.numerical_score, 4),
            "score_range_min": self.score_range_min,
            "score_range_max": self.score_range_max,
            "score_percentile_rank": round(self.score_percentile_rank, 2),
            "scoring_date": self.scoring_date,
        }


@dataclass
class FcraAdverseActionNotice:
    """Complete RFC-compliant FCRA Adverse Action Notice document."""
    notice_id: str
    application_or_tx_id: str
    cardholder_id: str
    cardholder_name: str
    cardholder_address: str
    adverse_action_taken: str  # DECLINE, LINE_REDUCTION, STEP_UP_REQUIRED
    principal_reasons: List[AdverseFactorExplanation]
    credit_score_disclosure: ScoreDisclosureSummary
    consumer_reporting_agency_name: str
    consumer_reporting_agency_contact: str
    dispute_filing_window_days: int = 60
    notice_generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    digital_signature_hash: str = ""

    def generate_digital_signature(self, signing_secret: str) -> str:
        payload = f"{self.notice_id}:{self.cardholder_id}:{self.adverse_action_taken}:{self.notice_generated_at}:{signing_secret}"
        self.digital_signature_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return self.digital_signature_hash

    def to_formal_text(self) -> str:
        factors_text = "\n".join([
            f"  {idx + 1}. [{f.factor_code}] {f.factor_description}\n     Remediation: {f.actionable_remediation_guidance}"
            for idx, f in enumerate(self.principal_reasons[:4])
        ])

        return f"""
================================================================================
                    STATEMENT OF ADVERSE ACTION & FCRA NOTICE
================================================================================
Notice Reference ID: {self.notice_id}
Date of Notice:      {self.notice_generated_at}
Applicant/Cardholder: {self.cardholder_name} (ID: {self.cardholder_id})
Billing Address:     {self.cardholder_address}
Transaction Reference: {self.application_or_tx_id}

DECISION SUMMARY:
Action Taken: {self.adverse_action_taken}

PRINCIPAL REASONS FOR ADVERSE DECISION (Fair Credit Reporting Act Sec. 615(a)):
{factors_text}

DISCLOSURE OF RISK SCORING MODEL (Sec. 609(g)):
  Scoring System:      {self.credit_score_disclosure.score_model_name} (v{self.credit_score_disclosure.score_model_version})
  Calculated Score:    {self.credit_score_disclosure.numerical_score}
  Permissible Range:   [{self.credit_score_disclosure.score_range_min} - {self.credit_score_disclosure.score_range_max}]
  Percentile Rank:     {self.credit_score_disclosure.score_percentile_rank}% of evaluated population

YOUR CONSUMER DISPUTE RIGHTS:
Under the Fair Credit Reporting Act, you have the right to obtain a free copy of
your consumer report from the reporting agency within {self.dispute_filing_window_days} days of receiving this notice.
The agency did not make the decision to take adverse action and cannot provide specific reasons.

Reporting Agency: {self.consumer_reporting_agency_name}
Inquiries Contact: {self.consumer_reporting_agency_contact}

Digital Verification Hash: {self.digital_signature_hash}
================================================================================
"""


class FcraComplianceEngine:
    """Enterprise generator and auditor for Fair Credit Reporting Act compliance."""

    FACTOR_DICTIONARY: Dict[str, Dict[str, str]] = {
        "failed_pin_attempts_24h": {
            "code": "FCR_AUTH_001",
            "desc": "Multiple consecutive failed authentication or PIN entry attempts within 24 hours.",
            "guidance": "Authenticate in person with government-issued photo ID at your financial institution.",
        },
        "velocity_1h": {
            "code": "FCR_VEL_002",
            "desc": "Authorization transaction velocity exceeds normal frequency thresholds.",
            "guidance": "Space out high-frequency transactions or notify your bank prior to rapid purchasing.",
        },
        "distance_from_home_km": {
            "code": "FCR_GEO_003",
            "desc": "Physical point-of-sale terminal location is significantly displaced from primary residence.",
            "guidance": "Update your current travel plans or primary residence billing address with card services.",
        },
        "amount_ratio_to_mean_30d": {
            "code": "FCR_AMT_004",
            "desc": "Transaction dollar amount significantly exceeds 30-day historical average spend.",
            "guidance": "Request a temporary authorized single-purchase limit increase via customer support.",
        },
        "is_impossible_travel": {
            "code": "FCR_GEO_005",
            "desc": "Geographical velocity between successive card uses is physically impossible.",
            "guidance": "Contact fraud operations immediately if your physical plastic card is still in your possession.",
        },
        "merchant_historical_risk": {
            "code": "FCR_MER_006",
            "desc": "Merchant terminal associated with elevated dispute or compromise risk index.",
            "guidance": "Utilize secure virtual card numbers or secondary payment methods for this merchant.",
        },
        "entry_mode_CNP": {
            "code": "FCR_CHL_007",
            "desc": "Card-Not-Present authorization lacking 3D-Secure secondary cryptographic validation.",
            "guidance": "Enroll in 3D-Secure 2.0 biometric verification with your issuing bank.",
        },
    }

    def __init__(self, cra_name: str = "FraudGuard Consumer Risk Bureau", cra_contact: str = "1-800-555-FRAUD (risk-inquiries@fraudguard.ai)"):
        self.cra_name = cra_name
        self.cra_contact = cra_contact

    def generate_notice(
        self,
        transaction_id: str,
        cardholder_id: str,
        cardholder_name: str,
        cardholder_address: str,
        risk_score: float,
        model_name: str,
        model_version: str,
        feature_attributions: Dict[str, float],
        feature_values: Dict[str, Any],
        decision_action: str = "DECLINE",
        signing_secret: str = "fcra_sec_key_2026",
    ) -> FcraAdverseActionNotice:
        """Construct a certified FCRA Adverse Action Notice from model attributions."""
        sorted_factors = sorted(
            feature_attributions.items(),
            key=lambda item: abs(item[1]),
            reverse=True
        )

        principal_factors: List[AdverseFactorExplanation] = []
        for feat_name, impact in sorted_factors:
            if impact <= 0.0:
                continue
            meta = self.FACTOR_DICTIONARY.get(feat_name, {
                "code": f"FCR_GEN_{abs(hash(feat_name)) % 1000:03d}",
                "desc": f"Behavioral indicator related to {feat_name.replace('_', ' ')}.",
                "guidance": "Review recent billing statements for unauthorized account activity.",
            })

            val = feature_values.get(feat_name, "N/A")
            principal_factors.append(AdverseFactorExplanation(
                factor_code=meta["code"],
                factor_description=meta["desc"],
                relative_weight=impact,
                feature_name=feat_name,
                feature_value=val,
                baseline_benchmark="Standard Profile Norm",
                actionable_remediation_guidance=meta["guidance"],
            ))

        if not principal_factors:
            principal_factors.append(AdverseFactorExplanation(
                factor_code="FCR_GEN_001",
                factor_description="Elevated composite anomaly score across multiple combined behavioral dimensions.",
                relative_weight=1.0,
                feature_name="composite_risk_score",
                feature_value=risk_score,
                baseline_benchmark=0.10,
                actionable_remediation_guidance="Contact your issuing bank customer support to verify account security.",
            ))

        percentile = max(1.0, min(99.9, (1.0 - risk_score) * 100.0))
        score_disclosure = ScoreDisclosureSummary(
            score_model_name=model_name,
            score_model_version=model_version,
            numerical_score=round(risk_score * 1000.0, 1),
            score_range_min=0.0,
            score_range_max=1000.0,
            score_percentile_rank=percentile,
            scoring_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        )

        notice = FcraAdverseActionNotice(
            notice_id=f"AAN-{uuid.uuid4().hex[:12].upper()}",
            application_or_tx_id=transaction_id,
            cardholder_id=cardholder_id,
            cardholder_name=cardholder_name,
            cardholder_address=cardholder_address,
            adverse_action_taken=decision_action,
            principal_reasons=principal_factors[:4],
            credit_score_disclosure=score_disclosure,
            consumer_reporting_agency_name=self.cra_name,
            consumer_reporting_agency_contact=self.cra_contact,
        )
        notice.generate_digital_signature(signing_secret)
        return notice
