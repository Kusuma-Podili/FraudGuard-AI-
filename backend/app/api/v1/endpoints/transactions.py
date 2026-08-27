"""Real-Time Transaction Inference, Scoring Gateway, and Historical Query Endpoints."""

import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.api.v1.deps import get_current_user
from backend.app.models.user import User
from backend.app.models.transaction import TransactionRecord
from backend.app.schemas.transaction import TransactionEvaluationRequest, DecisionResponse, TransactionResponse
from backend.app.schemas.common import APIResponse, PaginatedResponse
from backend.app.services.decision_engine import get_decision_engine
from backend.app.services.case_service import CaseService
from backend.app.streaming.websocket_manager import ws_manager

router = APIRouter()


@router.post("/score", response_model=APIResponse[DecisionResponse], summary="Real-Time Decision Gateway (<20ms)")
async def score_transaction(
    payload: TransactionEvaluationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Real-time transaction evaluation endpoint executing rules + feature store + ML ensemble."""
    engine = get_decision_engine()
    raw_dict = payload.model_dump()

    # 1. Execute sub-20ms decision evaluation
    eval_result = engine.evaluate_transaction(raw_dict)

    # 2. Asynchronously persist transaction to database
    tx_rec = TransactionRecord(
        transaction_id=eval_result["transaction_id"],
        card_id=payload.card_id,
        cardholder_id=payload.cardholder_id or f"USR_{payload.card_id[-5:]}",
        amount=payload.amount,
        currency=payload.currency,
        merchant_id=payload.merchant_id,
        merchant_name=payload.merchant_name,
        merchant_category=payload.merchant_category,
        entry_mode=payload.entry_mode,
        card_type=payload.card_type,
        card_network=payload.card_network,
        latitude=payload.latitude,
        longitude=payload.longitude,
        country_code=payload.country_code,
        device_fingerprint=payload.device_fingerprint,
        ip_address=payload.ip_address,
        risk_score=eval_result["risk_score"],
        decision_action=eval_result["decision_action"],
        risk_tier=eval_result["risk_tier"],
        triggered_rules=eval_result["triggered_rules"],
        model_breakdown=eval_result["model_breakdown"],
        fraud_archetype="ANOMALY" if eval_result["is_anomaly"] else "LEGITIMATE"
    )
    db.add(tx_rec)
    await db.commit()

    # 3. If action is DECLINE, REVIEW, or CHALLENGE_3DS, automatically raise Investigation Case
    if eval_result["decision_action"] in ("DECLINE", "REVIEW", "CHALLENGE_3DS"):
        asyncio.create_task(
            CaseService.create_case_for_transaction(
                db=db,
                transaction_id=eval_result["transaction_id"],
                card_id=payload.card_id,
                cardholder_id=payload.cardholder_id or f"USR_{payload.card_id[-5:]}",
                amount=payload.amount,
                risk_score=eval_result["risk_score"],
                decision_action=eval_result["decision_action"],
                evidence=eval_result
            )
        )

    # 4. Broadcast live stream event over WebSockets
    stream_payload = {
        "event": "TRANSACTION_PROCESSED",
        "transaction_id": eval_result["transaction_id"],
        "card_id": payload.card_id,
        "amount": payload.amount,
        "merchant_name": payload.merchant_name or payload.merchant_id,
        "category": payload.merchant_category,
        "risk_score": eval_result["risk_score"],
        "decision_action": eval_result["decision_action"],
        "risk_tier": eval_result["risk_tier"],
        "is_anomaly": eval_result["is_anomaly"],
        "latency_ms": eval_result["latency_ms"],
        "timestamp": eval_result["evaluated_at"],
    }
    asyncio.create_task(ws_manager.broadcast("transactions", stream_payload))

    decision_dto = DecisionResponse(
        transaction_id=eval_result["transaction_id"],
        decision_action=eval_result["decision_action"],
        risk_score=eval_result["risk_score"],
        risk_tier=eval_result["risk_tier"],
        confidence_level=eval_result["confidence_level"],
        triggered_rules=eval_result["triggered_rules"],
        model_breakdown=eval_result["model_breakdown"],
        is_anomaly=eval_result["is_anomaly"],
        is_impossible_travel=eval_result["is_impossible_travel"],
        requires_step_up_auth=eval_result["requires_step_up_auth"],
        latency_ms=eval_result["latency_ms"],
        evaluated_at=eval_result["evaluated_at"],
    )

    return APIResponse(data=decision_dto, message="Transaction evaluated successfully")


@router.get("", response_model=APIResponse[PaginatedResponse[TransactionResponse]], summary="Query Transactions")
async def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    min_score: Optional[float] = None,
    action: Optional[str] = None,
    card_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Query transactions with filtering and pagination."""
    query = select(TransactionRecord)
    count_query = select(func.count(TransactionRecord.id))

    if min_score is not None:
        query = query.where(TransactionRecord.risk_score >= min_score)
        count_query = count_query.where(TransactionRecord.risk_score >= min_score)
    if action:
        query = query.where(TransactionRecord.decision_action == action)
        count_query = count_query.where(TransactionRecord.decision_action == action)
    if card_id:
        query = query.where(TransactionRecord.card_id == card_id)
        count_query = count_query.where(TransactionRecord.card_id == card_id)

    total = (await db.execute(count_query)).scalar() or 0
    offset = (page - 1) * page_size
    query = query.order_by(desc(TransactionRecord.created_at)).offset(offset).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()
    total_pages = (total + page_size - 1) // page_size

    paginated = PaginatedResponse[TransactionResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
    return APIResponse(data=paginated)
