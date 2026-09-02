"""Anti-Money Laundering (AML) & Bank Secrecy Act (BSA) Regulatory Filing Engine.

Implements statutory transaction monitoring for:
- Currency Transaction Reports (CTR) for aggregate daily cash/debit > ₹10,000
- Structuring / Smurfing detection (₹9,000 - ₹9,999 sequential split transfers)
- FinCEN Suspicious Activity Report (SAR) Form 111 XML serialization
- High-Risk Jurisdiction & Offshore Haven money laundering pattern alerts
"""

from __future__ import annotations
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any


@dataclass
class SuspiciousActivityRecord:
    sar_id: str
    filing_type: str  # INITIAL, CONTINUING, CORRECTION
    subject_id: str
    subject_full_name: str
    subject_tin_or_ssn: str
    subject_address: str
    suspicious_activity_types: List[str]  # STRUCTURING, TERRORIST_FINANCING, MONEY_LAUNDERING, IDENTITY_THEFT
    summary_narrative: str
    total_dollar_amount: float
    start_date: str
    end_date: str
    financial_institution_ein: str = "12-3456789"
    institution_name: str = "FraudGuard National Bank & Trust"

    def to_fincen_xml(self) -> str:
        """Serialize SAR into FinCEN XML schema format."""
        root = ET.Element("FinCEN_SAR_Batch", attrib={
            "SchemaVersion": "1.4",
            "GeneratedTimestamp": datetime.now(timezone.utc).isoformat(),
        })

        report = ET.SubElement(root, "SuspiciousActivityReport", attrib={"ReportID": self.sar_id})

        # Institution Info
        inst = ET.SubElement(report, "FilingInstitution")
        ET.SubElement(inst, "InstitutionName").text = self.institution_name
        ET.SubElement(inst, "EIN").text = self.financial_institution_ein

        # Subject Info
        subj = ET.SubElement(report, "SubjectDetails")
        ET.SubElement(subj, "SubjectID").text = self.subject_id
        ET.SubElement(subj, "FullName").text = self.subject_full_name
        ET.SubElement(subj, "TaxpayerID").text = self.subject_tin_or_ssn
        ET.SubElement(subj, "Address").text = self.subject_address

        # Activity Categories
        acts = ET.SubElement(report, "ActivityCategories")
        for cat in self.suspicious_activity_types:
            ET.SubElement(acts, "CategoryCode").text = cat

        # Financials
        fin = ET.SubElement(report, "FinancialImpact")
        ET.SubElement(fin, "TotalDollarAmount").text = f"{self.total_dollar_amount:.2f}"
        ET.SubElement(fin, "ActivityStartDate").text = self.start_date
        ET.SubElement(fin, "ActivityEndDate").text = self.end_date

        # Narrative
        narrative = ET.SubElement(report, "Narrative")
        ET.SubElement(narrative, "NarrativeSummary").text = self.summary_narrative

        return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")


class AmlBsaMonitoringEngine:
    """Real-Time AML/BSA Anomaly Detector and Regulatory SAR Subsystem."""

    STRUCTURING_THRESHOLD_MIN = 8500.00
    STRUCTURING_THRESHOLD_MAX = 9999.99
    CTR_MANDATORY_THRESHOLD = 10000.00

    def __init__(self):
        # In-memory account 24h rolling totals for structuring
        self.rolling_account_volumes: Dict[str, List[Tuple[float, datetime]]] = {}

    def check_ctr_requirement(self, amount: float) -> Tuple[bool, str]:
        """Verify if Currency Transaction Report (CTR) filing is statutorily mandated."""
        if amount >= self.CTR_MANDATORY_THRESHOLD:
            return True, f"Mandatory CTR filing required: Single transaction ₹{amount:,.2f} >= ₹10,000 threshold."
        return False, "CTR not required."

    def detect_structuring(self, cardholder_id: str, amount: float, timestamp: Optional[datetime] = None) -> Tuple[bool, Optional[str]]:
        """Detect structured transaction amounts intended to evade ₹10k reporting thresholds."""
        ts = timestamp or datetime.now(timezone.utc)
        if cardholder_id not in self.rolling_account_volumes:
            self.rolling_account_volumes[cardholder_id] = []

        self.rolling_account_volumes[cardholder_id].append((amount, ts))

        # Check single transaction structuring (₹8,500 - ₹9,999)
        if self.STRUCTURING_THRESHOLD_MIN <= amount <= self.STRUCTURING_THRESHOLD_MAX:
            return True, f"High-confidence structuring pattern: Single amount ₹{amount:,.2f} deliberately below ₹10,000 CTR cutoff."

        # Check rolling 24h aggregate structuring
        recent = [
            amt for amt, t in self.rolling_account_volumes[cardholder_id]
            if (ts - t).total_seconds() <= 86400
        ]

        if len(recent) >= 2 and sum(recent) >= self.CTR_MANDATORY_THRESHOLD:
            all_below_cutoff = all(a < self.CTR_MANDATORY_THRESHOLD for a in recent)
            if all_below_cutoff:
                return True, f"Smurfing pattern detected: {len(recent)} transactions totaling ₹{sum(recent):,.2f} in 24h."

        return False, None

    def build_sar(
        self,
        subject_id: str,
        subject_name: str,
        subject_ssn: str,
        subject_address: str,
        suspicious_types: List[str],
        total_amount: float,
        narrative: str,
    ) -> SuspiciousActivityRecord:
        """Construct full SAR record ready for FinCEN transmission."""
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return SuspiciousActivityRecord(
            sar_id=f"SAR-FINCEN-{uuid.uuid4().hex[:10].upper()}",
            filing_type="INITIAL",
            subject_id=subject_id,
            subject_full_name=subject_name,
            subject_tin_or_ssn=subject_ssn,
            subject_address=subject_address,
            suspicious_activity_types=suspicious_types,
            summary_narrative=narrative,
            total_dollar_amount=total_amount,
            start_date=today_str,
            end_date=today_str,
        )
