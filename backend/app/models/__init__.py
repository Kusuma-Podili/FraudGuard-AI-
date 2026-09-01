"""SQLAlchemy Domain Models Registry."""

from backend.app.models.user import User, UserRole
from backend.app.models.transaction import TransactionRecord
from backend.app.models.case import InvestigationCase, CaseNote, CaseStatus, CaseSeverity
from backend.app.models.alert import AlertRecord, AlertSeverity, AlertStatus
from backend.app.models.customer import CustomerProfile, CustomerRiskTier
from backend.app.models.rule import FraudRule, RuleAction
from backend.app.models.model_registry import ModelRegistryRecord
from backend.app.models.merchant import MerchantEntity
from backend.app.models.chargeback import ChargebackDispute
from backend.app.models.audit_log import AuditLogRecord
from backend.app.models.settings import SystemSettingRecord

__all__ = [
    "User",
    "UserRole",
    "TransactionRecord",
    "InvestigationCase",
    "CaseNote",
    "CaseStatus",
    "CaseSeverity",
    "AlertRecord",
    "AlertSeverity",
    "AlertStatus",
    "CustomerProfile",
    "CustomerRiskTier",
    "FraudRule",
    "RuleAction",
    "ModelRegistryRecord",
    "MerchantEntity",
    "ChargebackDispute",
    "AuditLogRecord",
    "SystemSettingRecord",
]
