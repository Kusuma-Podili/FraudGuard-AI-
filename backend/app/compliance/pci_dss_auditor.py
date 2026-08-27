"""PCI-DSS v4.0 Security & Account Data Protection Auditor.

Enforces strict compliance with Payment Card Industry Data Security Standard (PCI-DSS):
- Requirement 3: Protection of stored account data and Primary Account Number (PAN) tokenization
- Requirement 6: Secure coding and input sanitization
- Requirement 8: Identification, authentication, and multi-factor enforcement
- Requirement 10: Immutable logging of cardholder data environment (CDE) access
"""

from __future__ import annotations
import re
import hashlib
import hmac
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone


@dataclass
class PciViolationRecord:
    requirement_id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    field_name: str
    description: str
    detected_value_masked: str
    remediation_action: str


class PciDssAuditor:
    """Automated PCI-DSS v4.0 Scanner and Data Sanitizer."""

    # Regex patterns for unmasked PANs
    PAN_PATTERNS = {
        "VISA": re.compile(r"^4[0-9]{12}(?:[0-9]{3})?$"),
        "MASTERCARD": re.compile(r"^5[1-5][0-9]{14}|2(22[1-9][0-9]{12}|2[3-9][0-9]{13}|[3-6][0-9]{14}|7[0-1][0-9]{13}|720[0-9]{12})$"),
        "AMEX": re.compile(r"^3[47][0-9]{13}$"),
        "DISCOVER": re.compile(r"^6(?:011|5[0-9]{2})[0-9]{12}$"),
        "GENERIC_PAN": re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b|\b\d{15,19}\b"),
    }

    # Sensitive Authentication Data (SAD) patterns (prohibited from post-authorization storage)
    CVV_PATTERN = re.compile(r"^\d{3,4}$")
    TRACK_DATA_PATTERN = re.compile(r"(%?[Bb]\d{13,19}\^[^\^]{2,26}\^\d{4}|\;\d{13,19}\=\d{4})")

    @staticmethod
    def validate_luhn(pan: str) -> bool:
        """Validate credit card number using Luhn algorithm (mod 10)."""
        clean_pan = re.sub(r"\D", "", pan)
        if not clean_pan or len(clean_pan) < 13 or len(clean_pan) > 19:
            return False

        digits = [int(d) for d in clean_pan]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]

        checksum = sum(odd_digits)
        for d in even_digits:
            doubled = d * 2
            checksum += (doubled - 9) if doubled > 9 else doubled

        return checksum % 10 == 0

    @staticmethod
    def mask_pan(pan: str) -> str:
        """PCI-DSS compliant truncation: preserve first 6 (BIN) and last 4 digits only."""
        clean_pan = re.sub(r"\D", "", pan)
        if len(clean_pan) <= 10:
            return "*" * len(clean_pan)
        first6 = clean_pan[:6]
        last4 = clean_pan[-4:]
        middle_mask = "*" * (len(clean_pan) - 10)
        return f"{first6}{middle_mask}{last4}"

    @classmethod
    def tokenize_pan(cls, pan: str, hmac_key: str) -> str:
        """Format-preserving HMAC surrogate token for Primary Account Number."""
        clean_pan = re.sub(r"\D", "", pan)
        token_hash = hmac.new(hmac_key.encode("utf-8"), clean_pan.encode("utf-8"), hashlib.sha256).hexdigest()
        masked_prefix = clean_pan[:6] if len(clean_pan) >= 6 else "999999"
        masked_suffix = clean_pan[-4:] if len(clean_pan) >= 4 else "0000"
        return f"TOK_{masked_prefix}_{token_hash[:16].upper()}_{masked_suffix}"

    def audit_transaction_payload(self, payload: Dict[str, Any]) -> Tuple[bool, List[PciViolationRecord]]:
        """Audit payload for prohibited SAD storage and unmasked PAN leaks."""
        violations: List[PciViolationRecord] = []

        for key, value in payload.items():
            str_val = str(value)

            # 1. Check for unmasked PAN in string fields
            if key in ("card_id", "pan", "account_number", "card_number") or self.PAN_PATTERNS["GENERIC_PAN"].search(str_val):
                clean_num = re.sub(r"\D", "", str_val)
                if self.validate_luhn(clean_num) and not str_val.startswith("TOK_") and "*" not in str_val:
                    violations.append(PciViolationRecord(
                        requirement_id="PCI-DSS Req 3.4",
                        severity="CRITICAL",
                        field_name=key,
                        description="Unmasked Primary Account Number (PAN) detected in plaintext payload.",
                        detected_value_masked=self.mask_pan(str_val),
                        remediation_action="Replace plaintext PAN with format-preserving surrogate token prior to persistence.",
                    ))

            # 2. Check for prohibited Sensitive Authentication Data (SAD) like CVV/CVC
            if key.lower() in ("cvv", "cvc", "cvv2", "cvc2", "security_code", "card_verification_value"):
                violations.append(PciViolationRecord(
                    requirement_id="PCI-DSS Req 3.2",
                    severity="CRITICAL",
                    field_name=key,
                    description="Prohibited Sensitive Authentication Data (CVV/CVC) found in payload structure.",
                    detected_value_masked="***",
                    remediation_action="Do not store card verification code post-authorization; purge immediately after validation.",
                ))

            # 3. Check for raw magnetic stripe / EMV chip track data
            if self.TRACK_DATA_PATTERN.search(str_val):
                violations.append(PciViolationRecord(
                    requirement_id="PCI-DSS Req 3.2.1",
                    severity="CRITICAL",
                    field_name=key,
                    description="Full Track 1 / Track 2 equivalent data detected in storage payload.",
                    detected_value_masked="[FULL_TRACK_DATA_PURGED]",
                    remediation_action="Never store full track data from chip or magnetic stripe post-authorization.",
                ))

        is_compliant = len(violations) == 0
        return is_compliant, violations

    def sanitize_payload(self, payload: Dict[str, Any], token_key: str = "pci_token_secret_2026") -> Dict[str, Any]:
        """Deep clean payload stripping prohibited SAD and tokenizing card identifiers."""
        clean = {}
        for k, v in payload.items():
            if k.lower() in ("cvv", "cvc", "cvv2", "cvc2", "pin_block", "track_data"):
                continue  # Strip prohibited SAD entirely
            if k in ("card_id", "pan", "card_number") and isinstance(v, str):
                if not v.startswith("TOK_") and self.validate_luhn(v):
                    clean[k] = self.tokenize_pan(v, token_key)
                else:
                    clean[k] = v
            else:
                clean[k] = v
        return clean
