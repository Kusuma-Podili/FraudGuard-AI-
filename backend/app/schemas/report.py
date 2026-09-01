"""Report Generation Pydantic Schemas."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ReportGenerateRequest(BaseModel):
    report_type: str  # DAILY_FRAUD, WEEKLY_FRAUD, MONTHLY_FRAUD, TRANSACTIONS, CASES, ALERTS, MODEL_PERFORMANCE
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    format: str = "JSON"  # JSON, CSV


class ReportSummaryDTO(BaseModel):
    report_id: str
    report_type: str
    generated_at: str
    date_range: str
    total_records: int
    metrics_summary: Dict[str, Any]
    preview_data: List[Dict[str, Any]]
    csv_download_url: Optional[str] = None
