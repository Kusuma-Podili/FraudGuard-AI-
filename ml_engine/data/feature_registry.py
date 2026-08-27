"""Feature Schema, Definitions, and Centralized Metadata Registry.

Guarantees consistency between training-time feature pipelines (offline) and
real-time sub-20ms inference pipelines (online).
"""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple


class FeatureDataType(str, Enum):
    NUMERICAL = "NUMERICAL"
    CATEGORICAL = "CATEGORICAL"
    CYCLICAL = "CYCLICAL"
    BOOLEAN = "BOOLEAN"
    EMBEDDING = "EMBEDDING"


class FeatureUpdateCadence(str, Enum):
    STREAMING_REALTIME = "STREAMING_REALTIME"  # Sub-second in-memory / Redis update
    BATCH_1H = "BATCH_1H"                     # Hourly aggregate
    BATCH_24H = "BATCH_24H"                   # Daily profile aggregate
    STATIC = "STATIC"                         # Static cardholder/merchant profile


@dataclass
class FeatureDefinition:
    """Metadata specification for a single feature."""
    name: str
    data_type: FeatureDataType
    cadence: FeatureUpdateCadence
    description: str
    default_value: Any
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_categories: Optional[List[str]] = None
    is_sensitive_pii: bool = False
    importance_weight: float = 1.0


class FeatureRegistry:
    """Centralized catalog and validator of all system features."""

    def __init__(self):
        self._registry: Dict[str, FeatureDefinition] = {}

    def register(self, feature: FeatureDefinition) -> FeatureDefinition:
        """Register a new feature definition."""
        self._registry[feature.name] = feature
        return feature

    def get(self, name: str) -> Optional[FeatureDefinition]:
        """Retrieve a feature definition by name."""
        return self._registry.get(name)

    def list_all(self) -> List[FeatureDefinition]:
        """List all registered features."""
        return list(self._registry.values())

    def get_by_cadence(self, cadence: FeatureUpdateCadence) -> List[FeatureDefinition]:
        """Filter features by update cadence."""
        return [f for f in self._registry.values() if f.cadence == cadence]

    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate an input payload against registered schema constraints."""
        errors = []
        for feat_name, definition in self._registry.items():
            val = record.get(feat_name)
            if val is None:
                continue

            if definition.data_type == FeatureDataType.NUMERICAL:
                if not isinstance(val, (int, float)):
                    errors.append(f"Feature '{feat_name}' expected float/int, got {type(val).__name__}")
                else:
                    if definition.min_value is not None and val < definition.min_value:
                        errors.append(f"Feature '{feat_name}' value {val} < min {definition.min_value}")
                    if definition.max_value is not None and val > definition.max_value:
                        errors.append(f"Feature '{feat_name}' value {val} > max {definition.max_value}")

            elif definition.data_type == FeatureDataType.CATEGORICAL:
                if definition.allowed_categories and str(val) not in definition.allowed_categories:
                    errors.append(f"Feature '{feat_name}' value '{val}' not in allowed categories")

        return len(errors) == 0, errors


# Initialize default enterprise fraud feature registry
default_registry = FeatureRegistry()

# 1. Transaction Core Numerical Features
default_registry.register(FeatureDefinition(
    name="amount",
    data_type=FeatureDataType.NUMERICAL,
    cadence=FeatureUpdateCadence.STREAMING_REALTIME,
    description="Transaction monetary amount in base currency (USD)",
    default_value=0.0,
    min_value=0.01,
    max_value=1_000_000.0,
    importance_weight=1.8
))

default_registry.register(FeatureDefinition(
    name="cardholder_age",
    data_type=FeatureDataType.NUMERICAL,
    cadence=FeatureUpdateCadence.STATIC,
    description="Age of the primary cardholder in years",
    default_value=35,
    min_value=18,
    max_value=120,
    importance_weight=0.6
))

default_registry.register(FeatureDefinition(
    name="distance_from_home_km",
    data_type=FeatureDataType.NUMERICAL,
    cadence=FeatureUpdateCadence.STREAMING_REALTIME,
    description="Haversine distance between transaction coordinates and cardholder billing address",
    default_value=0.0,
    min_value=0.0,
    max_value=25000.0,
    importance_weight=1.5
))

# 2. Sliding Window Velocity Features
default_registry.register(FeatureDefinition(
    name="velocity_1h",
    data_type=FeatureDataType.NUMERICAL,
    cadence=FeatureUpdateCadence.STREAMING_REALTIME,
    description="Number of transactions initiated on this card within the trailing 60 minutes",
    default_value=1,
    min_value=0,
    max_value=1000,
    importance_weight=1.6
))

default_registry.register(FeatureDefinition(
    name="velocity_24h",
    data_type=FeatureDataType.NUMERICAL,
    cadence=FeatureUpdateCadence.STREAMING_REALTIME,
    description="Number of transactions on this card within the trailing 24 hours",
    default_value=1,
    min_value=0,
    max_value=5000,
    importance_weight=1.4
))

default_registry.register(FeatureDefinition(
    name="amount_ratio_to_mean_30d",
    data_type=FeatureDataType.NUMERICAL,
    cadence=FeatureUpdateCadence.BATCH_24H,
    description="Ratio of current amount to cardholder's 30-day average transaction size",
    default_value=1.0,
    min_value=0.0,
    max_value=100.0,
    importance_weight=1.7
))

default_registry.register(FeatureDefinition(
    name="failed_pin_attempts_24h",
    data_type=FeatureDataType.NUMERICAL,
    cadence=FeatureUpdateCadence.STREAMING_REALTIME,
    description="Count of consecutive incorrect PIN / CVV / 3DS attempts in last 24h",
    default_value=0,
    min_value=0,
    max_value=20,
    importance_weight=1.9
))

# 3. Categorical Profile Features
default_registry.register(FeatureDefinition(
    name="merchant_category",
    data_type=FeatureDataType.CATEGORICAL,
    cadence=FeatureUpdateCadence.STREAMING_REALTIME,
    description="Industry classification of merchant (e.g. ELECTRONICS, GAMBLING, GROCERY)",
    default_value="GENERAL_RETAIL",
    allowed_categories=[
        "GROCERY", "ELECTRONICS", "LUXURY_JEWELRY", "GAMBLING", "CRYPTO_EXCHANGE",
        "GAS_STATION", "TRAVEL_AIRLINE", "RESTAURANT", "DIGITAL_GOODS", "GENERAL_RETAIL"
    ],
    importance_weight=1.3
))

default_registry.register(FeatureDefinition(
    name="entry_mode",
    data_type=FeatureDataType.CATEGORICAL,
    cadence=FeatureUpdateCadence.STREAMING_REALTIME,
    description="Point-of-Sale entry mechanism (CHIP, CONTACTLESS, SWIPE, CNP, E_COMMERCE)",
    default_value="E_COMMERCE",
    allowed_categories=["CHIP", "CONTACTLESS", "SWIPE", "CNP", "E_COMMERCE", "MANUAL_KEYED"],
    importance_weight=1.2
))

default_registry.register(FeatureDefinition(
    name="card_type",
    data_type=FeatureDataType.CATEGORICAL,
    cadence=FeatureUpdateCadence.STATIC,
    description="Card tier and funding type (CREDIT_PLATINUM, DEBIT_PREPAID, CORPORATE)",
    default_value="CREDIT_STANDARD",
    allowed_categories=["CREDIT_STANDARD", "CREDIT_PLATINUM", "CREDIT_INFINITE", "DEBIT_STANDARD", "DEBIT_PREPAID", "CORPORATE"],
    importance_weight=0.7
))

default_registry.register(FeatureDefinition(
    name="card_network",
    data_type=FeatureDataType.CATEGORICAL,
    cadence=FeatureUpdateCadence.STATIC,
    description="Payment card network",
    default_value="VISA",
    allowed_categories=["VISA", "MASTERCARD", "AMEX", "DISCOVER", "JCB", "UNIONPAY"],
    importance_weight=0.4
))

default_registry.register(FeatureDefinition(
    name="device_type",
    data_type=FeatureDataType.CATEGORICAL,
    cadence=FeatureUpdateCadence.STREAMING_REALTIME,
    description="Client originating device hardware/OS fingerprint",
    default_value="MOBILE_APP",
    allowed_categories=["MOBILE_APP", "MOBILE_BROWSER", "DESKTOP_BROWSER", "POS_TERMINAL", "ATM", "SMART_WATCH"],
    importance_weight=1.0
))

default_registry.register(FeatureDefinition(
    name="transaction_channel",
    data_type=FeatureDataType.CATEGORICAL,
    cadence=FeatureUpdateCadence.STREAMING_REALTIME,
    description="Channel medium of transaction",
    default_value="ONLINE",
    allowed_categories=["ONLINE", "IN_STORE", "ATM", "MOTO", "RECURRING_SUBSCRIPTION"],
    importance_weight=1.1
))

default_registry.register(FeatureDefinition(
    name="country_code",
    data_type=FeatureDataType.CATEGORICAL,
    cadence=FeatureUpdateCadence.STREAMING_REALTIME,
    description="ISO 3166-1 alpha-2 country of transaction origin",
    default_value="US",
    importance_weight=1.1
))
