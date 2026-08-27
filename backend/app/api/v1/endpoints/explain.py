"""Explainable AI (XAI) & SHAP Waterfall Attribution Endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np

from backend.app.db.session import get_db
from backend.app.api.v1.deps import get_current_user
from backend.app.models.user import User
from backend.app.models.transaction import TransactionRecord
from backend.app.schemas.ml_payloads import ExplainabilityRequest, ExplainabilityResponse, CounterfactualDTO
from backend.app.schemas.common import APIResponse
from ml_engine.data.feature_store import get_feature_store
from ml_engine.models.ensemble_pipeline import get_default_ensemble
from ml_engine.explainability.shap_explainer import ShapExplainer
from ml_engine.explainability.counterfactual import CounterfactualExplainer

router = APIRouter()


@router.post("", response_model=APIResponse[ExplainabilityResponse], summary="Explain Transaction Decision (SHAP / XAI)")
async def explain_transaction(
    payload: ExplainabilityRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Generate SHAP waterfall attribution, counterfactuals, and graph telemetry for a transaction."""
    fs = get_feature_store()
    ensemble = get_default_ensemble()

    raw_tx = payload.transaction_payload or {}
    tx_id = payload.transaction_id or raw_tx.get("transaction_id", "TX_SAMPLE")

    # If transaction_id is provided, retrieve from DB if payload empty
    if payload.transaction_id and not raw_tx:
        stmt = select(TransactionRecord).where(TransactionRecord.transaction_id == payload.transaction_id)
        result = await db.execute(stmt)
        record = result.scalars().first()
        if record:
            raw_tx = {
                "transaction_id": record.transaction_id,
                "card_id": record.card_id,
                "cardholder_id": record.cardholder_id,
                "amount": record.amount,
                "merchant_id": record.merchant_id,
                "merchant_category": record.merchant_category,
                "entry_mode": record.entry_mode,
                "latitude": record.latitude,
                "longitude": record.longitude,
                "country_code": record.country_code,
                "device_fingerprint": record.device_fingerprint,
                "ip_address": record.ip_address,
            }

    if not raw_tx:
        raw_tx = {
            "transaction_id": tx_id,
            "card_id": "CARD_DEMO_1001",
            "amount": 2450.0,
            "merchant_category": "ELECTRONICS",
            "entry_mode": "CNP",
            "country_code": "US",
            "failed_pin_attempts_24h": 2
        }

    # Enrich features
    enriched = fs.enrich_transaction(raw_tx)
    feat_vec = fs.get_feature_vector(enriched)

    # Compute prediction & explanation
    pred = ensemble.score_transaction(
        feature_vector=feat_vec,
        card_id=str(raw_tx.get("card_id", "")),
        device_id=str(raw_tx.get("device_fingerprint", "")),
        ip_address=str(raw_tx.get("ip_address", ""))
    )

    explainer = ShapExplainer(model=ensemble.xgb)
    shap_res = explainer.explain_transaction(feat_vec, raw_attributes=enriched)

    cf_explainer = CounterfactualExplainer(model=ensemble.xgb)
    cf_recs = cf_explainer.generate_counterfactual(enriched, current_score=pred.overall_fraud_score, feature_vector=feat_vec)

    cf_dtos = [
        CounterfactualDTO(
            feature_name=r.feature_name,
            original_value=r.original_value,
            recommended_value=r.recommended_value,
            change_description=r.change_description,
            is_actionable=r.is_actionable
        )
        for r in cf_recs
    ]

    graph_risk, graph_telem = ensemble.graph_detector.compute_ring_risk_score(
        card_id=str(raw_tx.get("card_id", "")),
        device_id=str(raw_tx.get("device_fingerprint", "")),
        ip_address=str(raw_tx.get("ip_address", ""))
    )

    response_dto = ExplainabilityResponse(
        transaction_id=tx_id,
        risk_score=pred.overall_fraud_score,
        base_value=shap_res.base_value,
        decision_action=pred.decision_action,
        top_risk_factors=shap_res.top_risk_factors,
        top_protective_factors=shap_res.top_protective_factors,
        waterfall=shap_res.to_dict()["waterfall"],
        counterfactuals=cf_dtos,
        graph_syndicate_detected=pred.graph_syndicate_flag,
        graph_ring_telemetry=graph_telem
    )

    return APIResponse(data=response_dto, message="SHAP explanation computed")
