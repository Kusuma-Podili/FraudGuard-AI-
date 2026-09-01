"""Reports Generation and Export API Endpoints."""

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.api.v1.deps import get_current_user
from backend.app.models.user import User
from backend.app.schemas.report import ReportGenerateRequest, ReportSummaryDTO
from backend.app.schemas.common import APIResponse
from backend.app.services.report_service import ReportService

router = APIRouter()


@router.post("/generate", response_model=APIResponse[ReportSummaryDTO], summary="Generate Fraud & Risk Report")
async def generate_report(
    req: ReportGenerateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Generate on-demand fraud, case, alert, or model performance report with metrics summary."""
    report = await ReportService.generate_report(db, req)
    return APIResponse(data=report)


@router.get("/export/csv", summary="Export Report as CSV")
async def export_report_csv(
    type: str = Query("DAILY_FRAUD", description="Report type (e.g. DAILY_FRAUD, TRANSACTIONS, CASES, ALERTS)"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Download report as raw RFC-4180 CSV file."""
    csv_content = await ReportService.export_csv(db, report_type=type)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=FraudGuard_{type.lower()}_report.csv"}
    )
