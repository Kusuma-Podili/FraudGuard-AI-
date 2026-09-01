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
  Filter,
  RefreshCw,
  UserCheck,
  ShieldAlert,
  CheckCircle2,
  XCircle,
  ArrowRight,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  FileCheck,
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
      await api.updateAlertStatus(alertId, "RESOLVED", "Alert reviewed and deemed non-fraudulent.");
      fetchAlerts();
    } catch (e) {
      console.error("Failed to resolve alert", e);
    }
  };

  const handleConvertToCase = async (alertId: string) => {
    try {
      await api.convertAlertToCase(alertId);
      fetchAlerts();
    } catch (e) {
      console.error("Failed to convert alert to case", e);
    }
  };

  const handleInvestigateAlert = async (alt: FraudAlert) => {
    try {
      const res = await api.getTransactionDetail(alt.transaction_id);
      if (res && res.transaction) {
        setInvestigationTx(res.transaction);
        setIsInvestigateOpen(true);
      }
    } catch {
      // Create fallback record for investigation modal
      setInvestigationTx({
        transaction_id: alt.transaction_id,
        card_id: alt.card_id,
        cardholder_id: alt.cardholder_id || f`USR_${alt.card_id.slice(-4)}`,
        amount: alt.amount,
        currency: "USD",
        merchant_id: "M_SAMPLE",
        merchant_name: alt.merchant_name || "Online Merchant",
        merchant_category: "ELECTRONICS",
        entry_mode: "CNP",
        risk_score: alt.risk_score,
        risk_tier: alt.severity,
        decision_action: "REVIEW",
        triggered_rules: alt.triggered_rules,
        fraud_archetype: "ANOMALY",
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
            <Bell className="w-6 h-6 text-red-400" />
            <h1 className="text-2xl font-bold text-gray-100 tracking-tight">Fraud Alert Center</h1>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Real-time security triggers, velocity violations, and impossible travel alerts requiring operator triage.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchAlerts} disabled={isLoading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filter Tabs & Search */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-2">
          {["ALL", "NEW", "ASSIGNED", "UNDER_REVIEW", "CASE_CREATED", "RESOLVED"].map((st) => (
            <button
              key={st}
              onClick={() => {
                setStatusFilter(st);
                setPage(1);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                statusFilter === st
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-500/20"
                  : "bg-gray-900 text-gray-400 hover:text-gray-200 border border-gray-800"
              }`}
            >
              {st.replace("_", " ")}
            </button>
          ))}
        </div>

        <form onSubmit={handleSearch} className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-4 h-4 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search alert ID, card, reason..."
              className="bg-gray-900 border border-gray-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500 w-64"
            />
          </div>
          <Button type="submit" size="sm">
            Search
          </Button>
        </form>
      </div>

      {/* Alerts Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-gray-300">
            <thead className="bg-gray-950/80 text-[11px] text-gray-400 uppercase tracking-wider border-b border-gray-800">
              <tr>
                <th className="py-3.5 px-4 font-semibold">Alert ID</th>
                <th className="py-3.5 px-4 font-semibold">Transaction / Card</th>
                <th className="py-3.5 px-4 font-semibold">Risk Score</th>
                <th className="py-3.5 px-4 font-semibold">Severity</th>
                <th className="py-3.5 px-4 font-semibold">Trigger Reason</th>
                <th className="py-3.5 px-4 font-semibold">Status</th>
                <th className="py-3.5 px-4 font-semibold">Assigned To</th>
                <th className="py-3.5 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {alerts.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-gray-500">
                    No fraud alerts match the selected criteria.
                  </td>
                </tr>
              ) : (
                alerts.map((alt) => {
                  const riskBadge = getRiskColor(alt.severity);
                  const maskedCard = `**** **** **** ${alt.card_id.slice(-4)}`;

                  return (
                    <tr key={alt.id} className="hover:bg-gray-900/40 transition-colors">
                      <td className="py-3.5 px-4 font-mono font-bold text-gray-200">
                        {alt.alert_id}
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="font-mono text-gray-200">{alt.transaction_id}</div>
                        <div className="text-[10px] text-gray-500 font-mono">{maskedCard}</div>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${riskBadge.bg} ${riskBadge.text} ${riskBadge.border}`}>
                          {alt.risk_score.toFixed(2)}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${alt.severity === "CRITICAL" ? "bg-red-950 text-red-400" : "bg-amber-950 text-amber-400"}`}>
                          {alt.severity}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 max-w-xs">
                        <p className="text-gray-200 font-medium truncate">{alt.reason}</p>
                        <p className="text-[10px] text-gray-500 truncate">{alt.merchant_name} • {formatCurrency(alt.amount)}</p>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-300 font-semibold text-[10px]">
                          {alt.status.replace("_", " ")}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-gray-300 font-medium">
                        {alt.assigned_analyst_name || (
                          <span className="text-gray-500 italic">Unassigned</span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 text-right space-x-1.5">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleInvestigateAlert(alt)}
                          className="text-[11px]"
                        >
                          Dossier
                        </Button>
                        {alt.status !== "CASE_CREATED" && alt.status !== "RESOLVED" && (
                          <>
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
                            <Button
                              variant="secondary"
                              size="sm"
                              onClick={() => handleConvertToCase(alt.alert_id)}
                              className="text-[11px] text-amber-300 border-amber-500/30"
                            >
                              Escalate
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleResolve(alt.alert_id)}
                              className="text-[11px] text-emerald-400 hover:text-emerald-300"
                            >
                              Resolve
                            </Button>
                          </>
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
        <div className="p-4 border-t border-gray-800 flex items-center justify-between text-xs text-gray-400">
          <div>
            Showing <strong className="text-gray-200">{(page - 1) * pageSize + 1}</strong> to{" "}
            <strong className="text-gray-200">{Math.min(page * pageSize, total)}</strong> of{" "}
            <strong className="text-gray-200">{total}</strong> alerts
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
            <span className="text-xs text-gray-300 font-medium px-2">
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
        title="Assign Alert to Analyst"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-xs text-gray-400">
            Select an operational fraud specialist to assign alert{" "}
            <strong className="text-gray-200">{selectedAlert?.alert_id}</strong>.
          </p>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-300">Fraud Analyst</label>
            <select
              value={analystName}
              onChange={(e) => setAnalystName(e.target.value)}
              className="w-full bg-gray-900 border border-gray-800 rounded-lg p-2 text-xs text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="Sarah Chen">Sarah Chen (Lead Fraud Analyst)</option>
              <option value="Marcus Vance">Marcus Vance (Senior Fraud Specialist)</option>
              <option value="Elena Rostova">Elena Rostova (Risk Strategy Lead)</option>
            </select>
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-gray-800">
            <Button variant="secondary" size="sm" onClick={() => setIsAssignModalOpen(false)}>
              Cancel
            </Button>
            <Button size="sm" onClick={handleAssign} disabled={assigning}>
              {assigning ? "Assigning..." : "Confirm Assignment"}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Investigation Dossier Modal */}
      <TransactionInvestigationModal
        isOpen={isInvestigateOpen}
        onClose={() => setIsInvestigateOpen(false)}
        transaction={investigationTx}
        onActionComplete={fetchAlerts}
      />
    </div>
  );
}
