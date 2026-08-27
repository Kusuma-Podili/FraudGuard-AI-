"""Fraud Analyst Workforce Management & Skill-Based Triage Dispatcher.

Handles analyst availability shifts, skill competencies (ATO specialist, AML investigator,
chargeback lead), workload load-balancing, and dynamic SLA deadline escalation timers.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any


@dataclass
class AnalystProfile:
    user_id: str
    full_name: str
    email: str
    skills: List[str]  # ATO, AML, HIGH_VALUE, CHARGEBACK_ARBITRATION, SYNDICATE
    is_active: bool = True
    current_assigned_cases_count: int = 0
    max_concurrent_capacity: int = 15
    average_resolution_time_minutes: float = 18.5
    accuracy_rating: float = 0.96


class WorkforceTriageDispatcher:
    """Dispatches incoming high-risk fraud cases to optimal available analysts."""

    def __init__(self):
        self.analysts: Dict[str, AnalystProfile] = {
            "USR_ANALYST_01": AnalystProfile(
                user_id="USR_ANALYST_01",
                full_name="Jane Doe",
                email="jane.doe@fraudguard.ai",
                skills=["ATO", "HIGH_VALUE", "SYNDICATE"],
                current_assigned_cases_count=4,
            ),
            "USR_ANALYST_02": AnalystProfile(
                user_id="USR_ANALYST_02",
                full_name="Alex Rivera",
                email="alex.rivera@fraudguard.ai",
                skills=["AML", "CHARGEBACK_ARBITRATION"],
                current_assigned_cases_count=2,
            ),
            "USR_ANALYST_03": AnalystProfile(
                user_id="USR_ANALYST_03",
                full_name="Sarah Chen",
                email="sarah.chen@fraudguard.ai",
                skills=["ATO", "AML", "HIGH_VALUE", "SYNDICATE"],
                current_assigned_cases_count=7,
            ),
        }

    def find_best_analyst_for_case(self, case_type: str, severity: str) -> Optional[AnalystProfile]:
        """Skill-based match prioritizing lowest current workload."""
        matching = [
            a for a in self.analysts.values()
            if a.is_active
            and case_type in a.skills
            and a.current_assigned_cases_count < a.max_concurrent_capacity
        ]

        if not matching:
            # Fallback to any active analyst with capacity
            matching = [a for a in self.analysts.values() if a.is_active and a.current_assigned_cases_count < a.max_concurrent_capacity]

        if not matching:
            return None

        # Sort by lowest active case count
        matching.sort(key=lambda a: a.current_assigned_cases_count)
        chosen = matching[0]
        chosen.current_assigned_cases_count += 1
        return chosen

    def compute_sla_expiry(self, severity: str) -> datetime:
        """Calculate SLA expiry timestamp based on triage priority."""
        now = datetime.now(timezone.utc)
        if severity.upper() == "CRITICAL":
            return now + timedelta(minutes=15)
        elif severity.upper() == "HIGH":
            return now + timedelta(hours=1)
        elif severity.upper() == "MEDIUM":
            return now + timedelta(hours=4)
        else:
            return now + timedelta(hours=24)
