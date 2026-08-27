"""Mastercard Integrated Processing Module (IPM) & First Presentment Processor.

Parses Mastercard clearing files, handles PDS (Private Data Sub-elements),
chargeback reason codes (4837 No Cardholder Authorization, 4853 Cardholder Dispute),
and MasterCom representment workflows.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class MastercardDisputeCode:
    code: str
    title: str
    chargeback_family: str  # FRAUD, CONSUMER, AUTHORIZATION
    reversal_deadline_days: int
    mastercom_cycle_type: str
    rebuttal_criteria: List[str]


class MastercardIpmProcessor:
    """Mastercard IPM message clearing and MasterCom dispute automation."""

    MASTERCARD_CODES: Dict[str, MastercardDisputeCode] = {
        "4837": MastercardDisputeCode(
            code="4837",
            title="No Cardholder Authorization (Fraudulent Transaction)",
            chargeback_family="FRAUD",
            reversal_deadline_days=45,
            mastercom_cycle_type="FIRST_CHARGEBACK",
            rebuttal_criteria=[
                "Evidence of EMV dynamic authentication",
                "3-D Secure SecureCode / Identity Check cryptographic proof (UCAF)",
                "Proof of digital delivery / physical signature confirmation",
            ],
        ),
        "4853": MastercardDisputeCode(
            code="4853",
            title="Cardholder Dispute (Defective / Not as Described / Services Cancelled)",
            chargeback_family="CONSUMER",
            reversal_deadline_days=45,
            mastercom_cycle_type="FIRST_CHARGEBACK",
            rebuttal_criteria=[
                "Proof of merchant refund policy disclosure prior to checkout",
                "Merchant cancellation terms agreement timestamp",
                "Cardholder communication logs proving agreement",
            ],
        ),
        "4808": MastercardDisputeCode(
            code="4808",
            title="Authorization Related Chargeback: Missing or Expired Authorization",
            chargeback_family="AUTHORIZATION",
            reversal_deadline_days=45,
            mastercom_cycle_type="FIRST_CHARGEBACK",
            rebuttal_criteria=["Valid authorization approval code (Field 38) and transmission STAN match"],
        ),
    }

    def decode_pds_subelements(self, raw_pds_string: str) -> Dict[str, str]:
        """Decode Mastercard Private Data Sub-elements (PDS tag-length-value stream)."""
        offset = 0
        parsed_pds = {}

        while offset < len(raw_pds_string) - 6:
            pds_tag = raw_pds_string[offset:offset + 4]
            pds_len = int(raw_pds_string[offset + 4:offset + 7])
            val = raw_pds_string[offset + 7:offset + 7 + pds_len]
            parsed_pds[pds_tag] = val
            offset += 7 + pds_len

        return parsed_pds

    def evaluate_mastercom_rebuttal(self, dispute_code: str, merchant_evidence: Dict[str, Any]) -> Tuple[bool, str, List[str]]:
        """Evaluate if merchant evidence meets MasterCom compelling representment criteria."""
        dispute_meta = self.MASTERCARD_CODES.get(dispute_code)
        if not dispute_meta:
            return False, f"Unknown dispute reason code {dispute_code}", []

        missing_evidence = []
        has_3ds = merchant_evidence.get("has_3ds_ucaf", False)
        has_delivery = merchant_evidence.get("has_delivery_proof", False)
        has_avs_cvv = merchant_evidence.get("avs_match", False) and merchant_evidence.get("cvv_match", False)

        if dispute_code == "4837":
            if not has_3ds and not (has_delivery and has_avs_cvv):
                missing_evidence.append("Missing either 3D-Secure UCAF token OR Verified Delivery Proof + AVS/CVV match.")

        is_eligible = len(missing_evidence) == 0
        status_msg = "Eligible for MasterCom Second Presentment (Pre-Arbitration Defense)" if is_eligible else "Ineligible: Insufficient compelling proof"
        return is_eligible, status_msg, missing_evidence
