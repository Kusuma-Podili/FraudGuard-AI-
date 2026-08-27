"""Visa Base II Clearing & Settlement Protocol Engine.

Implements Visa clearing draft format parsing (TC05, TC07, TC10, TC15, TC20),
Interchange qualification fee computation, and dispute reason code mapping.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class VisaDisputeReason:
    reason_code: str
    category: str  # FRAUD, AUTHORIZATION, PROCESSING_ERROR, CONSUMER_DISPUTE
    description: str
    time_limit_days: int
    compelling_evidence_rules: List[str]


class VisaBaseIIProcessor:
    """Visa Base II clearing, settlement interchange and dispute handling subsystem."""

    DISPUTE_REASON_CODES: Dict[str, VisaDisputeReason] = {
        "10.1": VisaDisputeReason(
            reason_code="10.1",
            category="FRAUD",
            description="EMV Liability Shift Counterfeit Fraud: Magstripe swipe fallback on chip-capable terminal.",
            time_limit_days=120,
            compelling_evidence_rules=["Proof of EMV chip interaction (Tag 9F26/9F27 cryptograms)", "ARQC validation"],
        ),
        "10.2": VisaDisputeReason(
            reason_code="10.2",
            category="FRAUD",
            description="EMV Liability Shift Non-Counterfeit Fraud: Chip card used without PIN verification.",
            time_limit_days=120,
            compelling_evidence_rules=["Cardholder verification method (CVM) list proof of PIN entry"],
        ),
        "10.3": VisaDisputeReason(
            reason_code="10.3",
            category="FRAUD",
            description="Other Fraud - Card-Present Environment: Cardholder denies authorization.",
            time_limit_days=120,
            compelling_evidence_rules=["Signed sales draft matching cardholder signature", "POS terminal imprint"],
        ),
        "10.4": VisaDisputeReason(
            reason_code="10.4",
            category="FRAUD",
            description="Other Fraud - Card-Absent Environment (CNP): E-commerce / Mail Order fraud dispute.",
            time_limit_days=120,
            compelling_evidence_rules=[
                "Evidence 3.0: Proof of prior undisputed transactions with matching IP/Device/Physical address",
                "AVS full match (Street and Zip exact match)",
                "CVV2 match and 3D-Secure CAVV authentication cryptographic token",
                "Delivery confirmation signature at verified billing address",
            ],
        ),
        "10.5": VisaDisputeReason(
            reason_code="10.5",
            category="FRAUD",
            description="Visa Fraud Monitoring Program (VFMP) threshold breach.",
            time_limit_days=60,
            compelling_evidence_rules=["Merchant remediation plan and portfolio fraud ratio reduction certification"],
        ),
        "13.1": VisaDisputeReason(
            reason_code="13.1",
            category="CONSUMER_DISPUTE",
            description="Merchandise/Services Not Received: Cardholder claims goods were never delivered.",
            time_limit_days=120,
            compelling_evidence_rules=["Carrier tracking number and signed proof of physical delivery"],
        ),
    }

    # Interchange fee rate table: (Base %, Fixed fee cents)
    INTERCHANGE_RATE_TABLE = {
        "CREDIT_CPS_RETAIL": (0.0151, 10),
        "CREDIT_CPS_ECOM_PREMIUM": (0.0195, 10),
        "CREDIT_CPS_SUPERMARKET": (0.0122, 5),
        "DEBIT_EXEMPT": (0.0005, 21),
        "DEBIT_REGULATED_DURBIN": (0.0005, 22),
    }

    def calculate_interchange(self, amount: float, card_type: str, entry_mode: str, is_durbin_regulated: bool = True) -> Tuple[float, str]:
        """Compute Visa interchange settlement cost for transaction."""
        if card_type.upper() == "DEBIT":
            rate_tier = "DEBIT_REGULATED_DURBIN" if is_durbin_regulated else "DEBIT_EXEMPT"
        else:
            if entry_mode.upper() == "CNP":
                rate_tier = "CREDIT_CPS_ECOM_PREMIUM"
            else:
                rate_tier = "CREDIT_CPS_RETAIL"

        rate_pct, fixed_cents = self.INTERCHANGE_RATE_TABLE.get(rate_tier, (0.0180, 10))
        fee = round((amount * rate_pct) + (fixed_cents / 100.0), 4)
        return fee, rate_tier

    def lookup_dispute_guidance(self, reason_code: str) -> Optional[VisaDisputeReason]:
        """Retrieve compelling evidence requirements for Visa dispute representment."""
        return self.DISPUTE_REASON_CODES.get(reason_code)
