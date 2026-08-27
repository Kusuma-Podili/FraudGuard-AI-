"""Alert Notification and Webhook Dispatcher Service."""

from typing import Dict, Any, List
from backend.app.core.logging import get_logger

logger = get_logger("fraudguard.notifications")


class NotificationService:
    """Dispatches webhook alerts and push notifications for high-priority fraud."""

    @staticmethod
    async def dispatch_critical_alert(
        transaction_id: str,
        amount: float,
        risk_score: float,
        action: str,
        rules: List[Dict[str, Any]]
    ) -> None:
        """Log or dispatch alert payload."""
        logger.info(
            f"DISPATCH ALERT: Transaction {transaction_id} flagged with {action} (Risk: {risk_score:.3f}). Rules: {[r.get('rule_code') for r in rules]}"
        )
