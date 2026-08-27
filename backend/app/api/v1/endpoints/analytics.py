"""Dashboard Analytics and Intelligence Endpoints."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.api.v1.deps import get_current_user
from backend.app.models.user import User
from backend.app.schemas.analytics import DashboardSummaryKPIs, HourlyFraudTrend, MerchantRiskProfileDTO, GeoRiskMetricDTO
from backend.app.schemas.common import APIResponse
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/summary", response_model=APIResponse[DashboardSummaryKPIs], summary="Executive KPI Summary")
async def get_summary_kpis(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Retrieve 24h counters, active threat status, and latency stats."""
    kpis = await AnalyticsService.get_summary_kpis(db)
    return APIResponse(data=kpis)


@router.get("/hourly-trends", response_model=APIResponse[List[HourlyFraudTrend]], summary="24h Hourly Fraud Trends")
async def get_hourly_trends(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get time-series fraud trend for charts."""
    trends = await AnalyticsService.get_hourly_trends(db)
    return APIResponse(data=trends)


@router.get("/merchants", response_model=APIResponse[List[MerchantRiskProfileDTO]], summary="Top Merchant Risk Profiles")
async def get_top_merchants(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get highest risk merchants."""
    merchants = await AnalyticsService.get_top_merchants(db)
    return APIResponse(data=merchants)


@router.get("/geo-heatmap", response_model=APIResponse[List[GeoRiskMetricDTO]], summary="Geographical Risk Map Data")
async def get_geo_heatmap(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get geographical coordinates and country-level risk indices."""
    geo_data = await AnalyticsService.get_geo_risk_heatmap(db)
    return APIResponse(data=geo_data)
