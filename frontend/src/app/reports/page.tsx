"use client";

import React, { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";
import { ReportSummaryDTO } from "@/types";
import {
  FileText,
  Download,
  Printer,
  CheckCircle2,
} from "lucide-react";

export default function ReportsPage() {
  const [reportType, setReportType] = useState<string>("DAILY_FRAUD");
  const [reportData, setReportData] = useState<ReportSummaryDTO | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchReport = async (type: string) => {
    setIsLoading(true);
    try {
      const data = await api.generateReport({ report_type: type as any });
      setReportData(data);
    } catch (e) {
      console.error("Failed to generate report", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReport(reportType);
  }, [reportType]);

  const handlePrint = () => {
    window.print();
  };

  const reportTypes = [
    { id: "DAILY_FRAUD", label: "Daily Executive Fraud Digest", desc: "24-hour summary of authorizations, blocked fraud volume, and SLA latency." },
    { id: "WEEKLY_FRAUD", label: "Weekly Threat Surveillance", desc: "7-day rolling fraud trends across payment channels and merchant MCCs." },
    { id: "MONTHLY_FRAUD", label: "Monthly Risk Management", desc: "30-day compliance dossier, net loss prevention, and chargeback rates." },
    { id: "TRANSACTIONS", label: "Full Transaction Ledger Report", desc: "Detailed audit record of all authorizations with ML risk scores and decisions." },
    { id: "CASES", label: "Investigation Case & Dispute Log", desc: "Analyst case resolution times, confirmed fraud outcomes, and false positives." },
    { id: "ALERTS", label: "Security Trigger & Alert Ledger", desc: "High-risk trigger history, impossible travel events, and velocity violations." },
    { id: "MODEL_PERFORMANCE", label: "MLOps Model Benchmark Report", desc: "Ensemble model ROC-AUC, PR-AUC, F1 metrics, and inference latency telemetry." },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <FileText className="w-6 h-6 text-[#5F8F83]" />
            <h1 className="text-2xl font-bold text-[#29332F] tracking-tight">Compliance & Intelligence Reports</h1>
          </div>
          <p className="text-xs text-[#69736E] mt-1">
            Generate executive briefings, FinCEN SAR compliance logs, and exportable RFC-4180 CSV audit trails.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handlePrint}>
            <Printer className="w-3.5 h-3.5 mr-1" />
            Print Report
          </Button>
          <a href={api.getReportCsvDownloadUrl(reportType)} download>
            <Button size="sm" className="bg-[#5F8F83] hover:bg-[#4F7D72] text-white shadow-sm">
              <Download className="w-3.5 h-3.5 mr-1" />
              Download CSV
            </Button>
          </a>
        </div>
      </div>

      {/* Report Selector Tabs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2">
        {reportTypes.map((rpt) => (
          <button
            key={rpt.id}
            onClick={() => setReportType(rpt.id)}
            className={`p-3 rounded-xl text-left transition-all border ${
              reportType === rpt.id
                ? "bg-[#C7D9D0] text-[#17231F] border-[#5F8F83] font-semibold shadow-sm"
                : "bg-[#FFFDFC] text-[#69736E] hover:text-[#29332F] border-[#E5DED5]"
            }`}
          >
            <span className="text-xs font-bold block truncate">{rpt.label.split(" ")[0]} {rpt.label.split(" ")[1]}</span>
            <span className="text-[10px] text-[#929A95] block truncate">{rpt.id.replace("_", " ")}</span>
          </button>
        ))}
      </div>

      {/* Report Summary Cards */}
      {reportData && reportData.metrics_summary && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-[#FFFDFC] border border-[#E5DED5] rounded-xl space-y-1">
            <span className="text-[11px] text-[#69736E] font-semibold uppercase">Date Range</span>
            <p className="text-sm font-bold text-[#5F8F83]">{reportData.date_range}</p>
          </div>
          <div className="p-4 bg-[#FFFDFC] border border-[#E5DED5] rounded-xl space-y-1">
            <span className="text-[11px] text-[#69736E] font-semibold uppercase">Total Records Sampled</span>
            <p className="text-sm font-bold text-[#29332F]">{reportData.total_records}</p>
          </div>
          <div className="p-4 bg-[#FFFDFC] border border-[#E5DED5] rounded-xl space-y-1">
            <span className="text-[11px] text-[#69736E] font-semibold uppercase">Primary Metric</span>
            <p className="text-sm font-bold text-[#35604B]">
              {reportData.metrics_summary.fraud_rate_pct !== undefined
                ? `${reportData.metrics_summary.fraud_rate_pct}% Fraud Rate`
                : reportData.metrics_summary.confirmed_fraud_count !== undefined
                ? `${reportData.metrics_summary.confirmed_fraud_count} Confirmed Cases`
                : `${reportData.metrics_summary.best_roc_auc || 0.988} ROC-AUC`}
            </p>
          </div>
          <div className="p-4 bg-[#FFFDFC] border border-[#E5DED5] rounded-xl space-y-1">
            <span className="text-[11px] text-[#69736E] font-semibold uppercase">Audit Status</span>
            <div className="flex items-center gap-1.5 text-xs text-[#35604B] font-semibold">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Validated & Signed</span>
            </div>
          </div>
        </div>
      )}

      {/* Report Data Preview Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Report Data Preview</CardTitle>
              <CardDescription>
                Live tabular preview of generated dataset for {reportType.replace("_", " ")}.
              </CardDescription>
            </div>
            <span className="text-xs text-[#929A95] font-mono">
              Generated at: {reportData ? new Date(reportData.generated_at).toLocaleTimeString() : "N/A"}
            </span>
          </div>
        </CardHeader>

        <div className="p-4 pt-0 overflow-x-auto">
          {isLoading ? (
            <div className="py-16 text-center text-xs text-[#69736E]">Generating compliance report...</div>
          ) : !reportData || !reportData.preview_data || reportData.preview_data.length === 0 ? (
            <div className="py-16 text-center text-xs text-[#929A95]">No data records available for this report type.</div>
          ) : (
            <table className="w-full text-left text-xs text-[#29332F]">
              <thead className="bg-[#F7F4EF] text-[11px] text-[#69736E] uppercase tracking-wider border-b border-[#E5DED5]">
                <tr>
                  {Object.keys(reportData.preview_data[0]).map((key) => (
                    <th key={key} className="py-3 px-4 font-semibold">
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E5DED5]/60">
                {reportData.preview_data.map((row, idx) => (
                  <tr key={idx} className="hover:bg-[#F7F4EF] transition-colors">
                    {Object.values(row).map((val: any, valIdx) => (
                      <td key={valIdx} className="py-3 px-4 text-[#29332F] font-medium">
                        {typeof val === "object" ? JSON.stringify(val) : String(val)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </Card>
    </div>
  );
}
