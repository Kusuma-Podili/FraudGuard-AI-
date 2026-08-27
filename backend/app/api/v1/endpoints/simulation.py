"""Real-Time Transaction Stream Simulator and Attack Sandbox Endpoints."""

import asyncio
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.api.v1.deps import get_current_user
from backend.app.models.user import User
from backend.app.schemas.analytics import SimulationControlRequest
from backend.app.schemas.common import APIResponse
from backend.app.streaming.websocket_manager import ws_manager
from ml_engine.data.dataset_generator import SyntheticTransactionGenerator
from backend.app.services.decision_engine import get_decision_engine

router = APIRouter()

# Global simulator state container
class SimulatorState:
    is_running: bool = False
    target_tps: int = 5
    total_generated: int = 0
    active_attack: Optional[str] = None
    task: Optional[asyncio.Task] = None


state = SimulatorState()
generator = SyntheticTransactionGenerator(seed=100)


async def _run_stream_worker():
    """Background loop generating transactions at target TPS and pushing to WebSockets."""
    from datetime import datetime, timezone
    engine = get_decision_engine()

    while state.is_running:
        interval = 1.0 / max(state.target_tps, 1)

        # Generate transaction
        force_fraud = bool(state.active_attack)
        tx = generator.generate_single_transaction(
            timestamp=datetime.now(timezone.utc),
            force_fraud=force_fraud,
            fraud_archetype=state.active_attack
        )

        eval_res = engine.evaluate_transaction(tx)
        state.total_generated += 1

        stream_item = {
            "event": "TRANSACTION_STREAMED",
            "transaction_id": eval_res["transaction_id"],
            "card_id": tx["card_id"],
            "amount": tx["amount"],
            "merchant_name": tx["merchant_name"],
            "category": tx["merchant_category"],
            "country": tx["country_code"],
            "risk_score": eval_res["risk_score"],
            "decision_action": eval_res["decision_action"],
            "risk_tier": eval_res["risk_tier"],
            "is_anomaly": eval_res["is_anomaly"],
            "is_impossible_travel": eval_res["is_impossible_travel"],
            "fraud_archetype": tx.get("fraud_archetype", "LEGITIMATE"),
            "latency_ms": eval_res["latency_ms"],
            "timestamp": eval_res["evaluated_at"],
        }
        await ws_manager.broadcast("transactions", stream_item)
        await asyncio.sleep(interval)


@router.post("/control", response_model=APIResponse[Dict[str, Any]], summary="Control Stream Simulator")
async def control_simulator(
    payload: SimulationControlRequest,
    user: User = Depends(get_current_user)
):
    """Start, stop, or change speed of background streaming generator."""
    if payload.action == "START":
        if not state.is_running:
            state.is_running = True
            state.target_tps = payload.target_tps or 5
            state.task = asyncio.create_task(_run_stream_worker())
    elif payload.action == "STOP":
        state.is_running = False
        state.active_attack = None
        if state.task:
            state.task.cancel()
            state.task = None
    elif payload.action == "SET_SPEED":
        state.target_tps = payload.target_tps or 5
    elif payload.action == "INJECT_ATTACK":
        state.active_attack = payload.attack_type or "CARD_TESTING"
        # Reset attack after duration if specified
        if payload.duration_seconds:
            async def _reset_attack():
                await asyncio.sleep(payload.duration_seconds)
                state.active_attack = None
            asyncio.create_task(_reset_attack())

    return APIResponse(data={
        "is_running": state.is_running,
        "target_tps": state.target_tps,
        "active_attack": state.active_attack,
        "total_generated": state.total_generated,
    }, message=f"Simulator action '{payload.action}' applied")


@router.get("/status", response_model=APIResponse[Dict[str, Any]], summary="Simulator Status")
async def get_simulator_status(
    user: User = Depends(get_current_user)
):
    """Retrieve active simulator status."""
    return APIResponse(data={
        "is_running": state.is_running,
        "target_tps": state.target_tps,
        "active_attack": state.active_attack,
        "total_generated": state.total_generated,
    })


@router.websocket("/ws")
async def websocket_stream_endpoint(websocket: WebSocket):
    """WebSocket endpoint streaming live real-time transactions to the frontend."""
    await ws_manager.connect(websocket, channel="transactions")
    try:
        while True:
            # Keep connection alive receiving ping/pong or client messages
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, channel="transactions")
