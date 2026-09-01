export interface ReportGenerateRequest {
  report_type:
    | "DAILY_FRAUD"
    | "WEEKLY_FRAUD"
    | "MONTHLY_FRAUD"
    | "TRANSACTIONS"
    | "CASES"
    | "ALERTS"
    | "MODEL_PERFORMANCE";
  start_date?: string;
  end_date?: string;
  format?: string;
}

export interface ReportSummaryDTO {
  report_id: string;
  report_type: string;
  generated_at: string;
  date_range: string;
  total_records: number;
  metrics_summary: Record<string, any>;
  preview_data: Record<string, any>[];
  csv_download_url?: string;
}
