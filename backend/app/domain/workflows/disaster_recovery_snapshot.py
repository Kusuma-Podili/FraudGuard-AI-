"""Enterprise Financial Workflow & State Machine: DisasterRecoverySnapshotter."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
import uuid


@dataclass
class DisasterRecoverySnapshotterState:
    workflow_id: str
    current_state: str
    transition_history: List[Dict[str, Any]] = field(default_factory=list)
    is_terminal: bool = False
    context_payload: Dict[str, Any] = field(default_factory=dict)


class DisasterRecoverySnapshotter:
    """Deterministic finite state machine for State Snapshotting & Zero-Data-Loss Failover."""

    VALID_STATES = ["INITIALIZED", "IN_PROGRESS", "AWAITING_REVIEW", "APPROVED", "REJECTED", "ESCALATED", "ARCHIVED"]

    def __init__(self, workflow_name: str = "DisasterRecoverySnapshotter"):
        self.workflow_name = workflow_name

    def create_instance(self, initial_payload: Dict[str, Any]) -> DisasterRecoverySnapshotterState:
        w_id = f"WF-{uuid.uuid4().hex[:10].upper()}"
        state = DisasterRecoverySnapshotterState(
            workflow_id=w_id,
            current_state="INITIALIZED",
            context_payload=initial_payload,
        )
        state.transition_history.append({
            "from_state": None,
            "to_state": "INITIALIZED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trigger": "INITIALIZE",
        })
        return state

    def transition(self, state: DisasterRecoverySnapshotterState, next_state: str, actor_id: str, reason: str) -> bool:
        if next_state not in self.VALID_STATES:
            return False

        prev = state.current_state
        state.current_state = next_state
        state.is_terminal = next_state in ("APPROVED", "REJECTED", "ARCHIVED")

        state.transition_history.append({
            "from_state": prev,
            "to_state": next_state,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": actor_id,
            "reason": reason,
        })
        return True
