"""Online Feature Caching and Redis Connector Service."""

from typing import Dict, Any, Optional
from backend.app.core.config import settings
from ml_engine.data.feature_store import get_feature_store, FeatureStore


class FeatureService:
    """Provides low-latency access to online feature store."""

    def __init__(self):
        self.feature_store = get_feature_store()

    def get_enriched_features(self, raw_tx: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich raw payload with real-time sliding-window counters."""
        return self.feature_store.enrich_transaction(raw_tx)
