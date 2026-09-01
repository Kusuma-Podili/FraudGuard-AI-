"""Unified API V1 Router."""

from fastapi import APIRouter

from backend.app.api.v1.endpoints import (
    auth,
    transactions,
    alerts,
    cases,
    customers,
    rules,
    models,
    explain,
    simulation,
    analytics,
    reports,
    users,
    settings,
    audit,
    merchants,
    health,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & RBAC"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions & Real-Time Scoring"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Fraud Alerts & Triage"])
api_router.include_router(cases.router, prefix="/cases", tags=["Investigation Case Management"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customer & Card 360 Profiling"])
api_router.include_router(rules.router, prefix="/rules", tags=["Dynamic Business Rules"])
api_router.include_router(models.router, prefix="/models", tags=["MLOps & Model Registry"])
api_router.include_router(explain.router, prefix="/explain", tags=["Explainable AI (SHAP / XAI)"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["Transaction Simulator & Attacks"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Fraud Analytics & Intelligence"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports & Compliance Exports"])
api_router.include_router(users.router, prefix="/users", tags=["Admin User Management"])
api_router.include_router(settings.router, prefix="/settings", tags=["System Settings & Thresholds"])
api_router.include_router(audit.router, prefix="/audit", tags=["Compliance Audit Logs"])
api_router.include_router(merchants.router, prefix="/merchants", tags=["Merchant Entity Management"])
api_router.include_router(health.router, prefix="/health", tags=["Health & Liveness Probes"])
