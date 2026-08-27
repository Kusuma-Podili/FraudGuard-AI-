"""Chargeback Arbitration & Representment Evidence Packaging Engine.

Compiles automated representment packets for Visa Pre-Arbitration and Mastercard MasterCom,
calculating win-rate probabilities and aggregating delivery confirmation, AVS/CVV receipts,
IP geolocations, and 3DS cryptographic authentication proofs.
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any


@dataclass
class RepresentmentDocument:
    doc_id: str
    doc_type: str  # INVOICE, CARRIER_DELIVERY_PROOF, CUSTOMER_CHAT, REFUND_POLICY, 3DS_CAVV
    filename: str
    uploaded_at: str
    sha256_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DisputeCaseRepresentment:
    representment_id: str
    case_id: str
    chargeback_amount: float
    currency: str
    dispute_reason_code: str
    card_network: str  # VISA, MASTERCARD, AMEX, DISCOVER
    merchant_id: str
    evidence_documents: List[RepresentmentDocument] = field(default_factory=list)
    rebuttal_letter_text: str = ""
    estimated_win_probability: float = 0.0
    status: str = "DRAFT"  # DRAFT, SUBMITTED_TO_NETWORK, WON, LOST, PRE_ARBITRATION

    def compile_formal_rebuttal(self) -> str:
        """Generate structured legal rebuttal letter for card network arbitration."""
        docs_summary = "\n".join([
            f"  - Exhibit {i+1} [{doc.doc_type}]: {doc.filename} (Hash: {doc.sha256_hash[:12]}...)"
            for i, doc in enumerate(self.evidence_documents)
        ])

        self.rebuttal_letter_text = f"""
================================================================================
           FORMAL CHARGEBACK REPRESENTMENT & EVIDENCE SUBMISSION
================================================================================
Representment Ref: {self.representment_id}
Case Reference:    {self.case_id}
Merchant Account:  {self.merchant_id}
Card Network:      {self.card_network}
Reason Code:       {self.dispute_reason_code}
Disputed Amount:   {self.currency} {self.chargeback_amount:,.2f}
Submission Date:   {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')}

REPRESENTMENT SUMMARY & MERCHANDISE DISPUTE DEFENSE:
The merchant hereby disputes the validity of chargeback reason {self.dispute_reason_code}.
The cardholder authorized the transaction in accordance with Visa/Mastercard Operating
Regulations. The goods/services were successfully provisioned and delivered to the verified
billing address of the legitimate cardholder.

ATTACHED EVIDENCE EXHIBITS:
{docs_summary if self.evidence_documents else '  - No documents attached yet.'}

ESTIMATED WIN PROBABILITY SCORE: {self.estimated_win_probability * 100:.1f}%

REQUEST FOR REVERSAL:
We formally request that the acquiring bank debit the cardholder and credit the merchant
in full for the disputed amount of {self.currency} {self.chargeback_amount:,.2f}.
================================================================================
"""
        return self.rebuttal_letter_text


class ChargebackArbitrationManager:
    """Manages representment lifecycle, compelling evidence scoring, and arbitration filings."""

    def evaluate_win_probability(self, network: str, reason_code: str, evidence: Dict[str, Any]) -> float:
        """Calculate statistical probability of winning representment."""
        score = 0.30  # Baseline

        if evidence.get("has_3ds_liability_shift", False):
            score += 0.45
        if evidence.get("has_signed_delivery_proof", False):
            score += 0.20
        if evidence.get("avs_match", False) and evidence.get("cvv_match", False):
            score += 0.15
        if evidence.get("prior_undisputed_tx_count", 0) >= 2:
            score += 0.20  # Visa Compelling Evidence 3.0 rule

        return min(0.98, max(0.05, score))

    def create_representment(
        self,
        case_id: str,
        amount: float,
        currency: str,
        reason_code: str,
        network: str,
        merchant_id: str,
        evidence: Dict[str, Any],
    ) -> DisputeCaseRepresentment:
        """Construct full representment case with win probability scoring."""
        prob = self.evaluate_win_probability(network, reason_code, evidence)
        rep = DisputeCaseRepresentment(
            representment_id=f"REP-{uuid.uuid4().hex[:10].upper()}",
            case_id=case_id,
            chargeback_amount=amount,
            currency=currency,
            dispute_reason_code=reason_code,
            card_network=network,
            merchant_id=merchant_id,
            estimated_win_probability=round(prob, 4),
        )
        rep.compile_formal_rebuttal()
        return rep
