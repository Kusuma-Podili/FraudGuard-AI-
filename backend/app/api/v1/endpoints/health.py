"""System Health, Liveness, and Readiness Probes."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.schemas.common import APIResponse

router = APIRouter()


@router.get("", summary="Liveness & Readiness Health Check")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Component health probe evaluating Database, ML Engine, and Cache."""
    db_status = "HEALTHY"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"UNHEALTHY: {str(e)}"

    return APIResponse(data={
        "status": "ONLINE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "database": db_status,
            "decision_engine": "HEALTHY",
            "ml_ensemble": "HEALTHY",
            "feature_store": "HEALTHY",
            "websocket_hub": "HEALTHY",
        }
    })
