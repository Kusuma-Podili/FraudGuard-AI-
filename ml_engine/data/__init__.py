"""Data generation, preprocessing, feature engineering, and feature store modules."""

from ml_engine.data.geodistance import calculate_haversine_distance, calculate_travel_velocity
from ml_engine.data.preprocessors import TabularPreprocessor, CyclicalTimeEncoder, RobustOutlierScaler
from ml_engine.data.balance_handlers import BalanceHandler, SMOTEHandler, ClassWeightCalculator
from ml_engine.data.feature_registry import FeatureDefinition, FeatureRegistry, default_registry
from ml_engine.data.velocity_engine import VelocityEngine, CardholderVelocityProfile
from ml_engine.data.feature_store import FeatureStore, get_feature_store
from ml_engine.data.dataset_generator import SyntheticTransactionGenerator, generate_fraud_dataset

__all__ = [
    "calculate_haversine_distance",
    "calculate_travel_velocity",
    "TabularPreprocessor",
    "CyclicalTimeEncoder",
    "RobustOutlierScaler",
    "BalanceHandler",
    "SMOTEHandler",
    "ClassWeightCalculator",
    "FeatureDefinition",
    "FeatureRegistry",
    "default_registry",
    "VelocityEngine",
    "CardholderVelocityProfile",
    "FeatureStore",
    "get_feature_store",
    "SyntheticTransactionGenerator",
    "generate_fraud_dataset",
]

