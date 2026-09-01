"use client";

import React, { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { TransactionInvestigationModal } from "@/components/transactions/TransactionInvestigationModal";
import { api } from "@/lib/api";
import { FraudAlert, TransactionRecord } from "@/types";
import { formatCurrency, getRiskColor, formatTimeAgo } from "@/lib/utils";
import {
  Bell,
  Search,
  RefreshCw,
  UserCheck,
  ChevronLeft,
  ChevronRight,
  Eye,
} from "lucide-react";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<FraudAlert[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  // Filters
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [search, setSearch] = useState("");

  // Assign Modal
  const [selectedAlert, setSelectedAlert] = useState<FraudAlert | null>(null);
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [analystName, setAnalystName] = useState("Sarah Chen");
  const [assigning, setAssigning] = useState(false);

  // Investigation Modal
  const [investigationTx, setInvestigationTx] = useState<TransactionRecord | null>(null);
  const [isInvestigateOpen, setIsInvestigateOpen] = useState(false);

  const fetchAlerts = async () => {
    setIsLoading(true);
    try {
      const res = await api.listAlerts({
        page,
        page_size: pageSize,
        status: statusFilter !== "ALL" ? statusFilter : undefined,
        severity: severityFilter !== "ALL" ? severityFilter : undefined,
        search: search || undefined,
      });
      setAlerts(res.items || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (e) {
      console.error("Failed to load alerts", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [page, pageSize, statusFilter, severityFilter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchAlerts();
  };

  const handleAssign = async () => {
    if (!selectedAlert) return;
    setAssigning(true);
    try {
      await api.assignAlert(selectedAlert.alert_id, "USR_ANALYST_01", analystName);
      setIsAssignModalOpen(false);
      fetchAlerts();
    } catch (e) {
      console.error("Assignment failed", e);
    } finally {
      setAssigning(false);
    }
  };

  const handleResolve = async (alertId: string) => {
    try {
      await api.updateAlertStatus(alertId, "RESOLVED", "Alert reviewed and verified.");
      fetchAlerts();
    } catch (e) {
      console.error("Failed to resolve alert", e);
    }
  };

  const handleOpenTx = async (alt: FraudAlert) => {
    try {
      const res = await api.getTransactionDetail(alt.transaction_id);
      if (res && res.transaction) {
        setInvestigationTx(res.transaction);
        setIsInvestigateOpen(true);
      }
    } catch {
      setInvestigationTx({
        transaction_id: alt.transaction_id,
        card_id: alt.card_id,
        amount: 3850.0,
        currency: "USD",
        merchant_name: "Online Merchant",
        merchant_category: "ELECTRONICS",
        entry_mode: "CNP",
        risk_score: alt.risk_score,
        risk_tier: alt.severity,
        decision_action: "REVIEW",
        triggered_rules: ["RULE_AMT_003"],
        created_at: alt.created_at,
      } as any);
      setIsInvestigateOpen(true);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Bell className="w-6 h-6 text-[#5F8F83]" />
            <h1 className="text-2xl font-bold text-[#29332F] tracking-tight">Fraud Alert Center</h1>
          </div>
          <p className="text-xs text-[#69736E] mt-1">
            Real-time security trigger ledger, velocity anomalies, and credential brute force alerts.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchAlerts} disabled={isLoading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filter Control */}
      <Card className="p-4 bg-[#FFFDFC] border-[#E5DED5]">
        <form onSubmit={handleSearch} className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[220px]">
            <Search className="w-4 h-4 text-[#929A95] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search alert reason, card number (e.g. 4829), Tx ID..."
              className="w-full bg-[#F7F4EF] border border-[#E5DED5] rounded-lg pl-9 pr-3 py-1.5 text-xs text-[#29332F] placeholder-[#929A95] focus:outline-none focus:ring-1 focus:ring-[#5F8F83]"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="bg-[#F7F4EF] border border-[#E5DED5] rounded-lg px-3 py-1.5 text-xs text-[#29332F] focus:outline-none focus:ring-1 focus:ring-[#5F8F83]"
          >
            <option value="ALL">All Statuses</option>
            <option value="NEW">NEW (Unassigned)</option>
            <option value="ASSIGNED">ASSIGNED (In Progress)</option>
            <option value="RESOLVED">RESOLVED</option>
            <option value="DISMISSED">DISMISSED</option>
          </select>

          <select
            value={severityFilter}
            onChange={(e) => {
              setSeverityFilter(e.target.value);
              setPage(1);
            }}
            className="bg-[#F7F4EF] border border-[#E5DED5] rounded-lg px-3 py-1.5 text-xs text-[#29332F] focus:outline-none focus:ring-1 focus:ring-[#5F8F83]"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>

          <Button type="submit" size="sm">
            Filter
          </Button>
        </form>
      </Card>

      {/* Alerts Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-[#29332F]">
            <thead className="bg-[#F7F4EF] text-[11px] text-[#69736E] uppercase tracking-wider border-b border-[#E5DED5]">
              <tr>
                <th className="py-3.5 px-4 font-semibold">Alert ID</th>
                <th className="py-3.5 px-4 font-semibold">Transaction / Masked Card</th>
                <th className="py-3.5 px-4 font-semibold">Risk Score</th>
                <th className="py-3.5 px-4 font-semibold">Severity</th>
                <th className="py-3.5 px-4 font-semibold">Reason</th>
                <th className="py-3.5 px-4 font-semibold">Status</th>
                <th className="py-3.5 px-4 font-semibold">Assigned Analyst</th>
                <th className="py-3.5 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E5DED5]/60">
              {alerts.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-[#929A95]">
                    No security alerts found matching query criteria.
                  </td>
                </tr>
              ) : (
                alerts.map((alt) => {
                  const riskColors = getRiskColor(alt.severity);
                  const maskedCard = `**** **** **** ${alt.card_id.slice(-4)}`;

                  return (
                    <tr key={alt.id} className="hover:bg-[#F7F4EF] transition-colors">
                      <td className="py-3.5 px-4 font-mono font-bold text-[#29332F]">{alt.alert_id}</td>
                      <td className="py-3.5 px-4">
                        <div className="font-mono text-[#29332F] font-bold">{alt.transaction_id}</div>
                        <div className="text-[10px] text-[#69736E] font-mono">{maskedCard}</div>
                      </td>
                      <td className="py-3.5 px-4 font-mono font-bold text-[#7B3030]">
                        {(alt.risk_score * 100).toFixed(1)}%
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${riskColors.badge}`}>
                          {alt.severity}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 max-w-xs truncate text-[#29332F] font-medium">
                        {alt.reason}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="px-2 py-0.5 rounded bg-[#DCE7E1] text-[#26332F] font-bold text-[10px]">
                          {alt.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-[#69736E]">
                        {alt.assigned_analyst_name || <span className="text-[#929A95] italic">Unassigned</span>}
                      </td>
                      <td className="py-3.5 px-4 text-right space-x-1.5">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleOpenTx(alt)}
                          className="text-[11px]"
                        >
                          <Eye className="w-3 h-3 mr-1 text-[#5F8F83]" />
                          Dossier
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedAlert(alt);
                            setIsAssignModalOpen(true);
                          }}
                          className="text-[11px]"
                        >
                          Assign
                        </Button>
                        {alt.status !== "RESOLVED" && (
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => handleResolve(alt.alert_id)}
                            className="text-[11px] text-[#35604B]"
                          >
                            Resolve
                          </Button>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 border-t border-[#E5DED5] flex items-center justify-between text-xs text-[#69736E]">
          <div>
            Showing <strong className="text-[#29332F]">{(page - 1) * pageSize + 1}</strong> to{" "}
            <strong className="text-[#29332F]">{Math.min(page * pageSize, total)}</strong> of{" "}
            <strong className="text-[#29332F]">{total}</strong> alerts
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(p - 1, 1))}
              disabled={page <= 1}
            >
              <ChevronLeft className="w-4 h-4" />
              Previous
            </Button>
            <span className="text-xs text-[#29332F] font-medium px-2">
              Page {page} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
              disabled={page >= totalPages}
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </Card>

      {/* Assign Modal */}
      <Modal
        isOpen={isAssignModalOpen}
        onClose={() => setIsAssignModalOpen(false)}
        title={`Assign Alert ${selectedAlert?.alert_id}`}
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-xs text-[#69736E]">
            Assign security alert to a dedicated fraud triage specialist.
          </p>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-[#29332F]">Select Analyst</label>
            <select
              value={analystName}
              onChange={(e) => setAnalystName(e.target.value)}
              className="w-full bg-[#F7F4EF] border border-[#E5DED5] rounded-lg p-2 text-xs text-[#29332F] focus:outline-none focus:ring-1 focus:ring-[#5F8F83]"
            >
              <option value="Sarah Chen">Sarah Chen (Lead Fraud Analyst)</option>
              <option value="Marcus Vance">Marcus Vance (Senior Specialist)</option>
              <option value="Elena Rostova">Elena Rostova (Risk Lead)</option>
            </select>
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-[#E5DED5]">
            <Button variant="secondary" size="sm" onClick={() => setIsAssignModalOpen(false)}>
              Cancel
            </Button>
            <Button size="sm" onClick={handleAssign} disabled={assigning}>
              {assigning ? "Assigning..." : "Confirm Assignment"}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Investigation Modal */}
      <TransactionInvestigationModal
        isOpen={isInvestigateOpen}
        onClose={() => setIsInvestigateOpen(false)}
        transaction={investigationTx}
        onActionComplete={fetchAlerts}
      />
    </div>
  );
}
