"use client";

import React, { useState } from "react";
import { useCases } from "@/hooks/useCases";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Select } from "@/components/ui/Select";
import { TransactionInvestigationModal } from "@/components/transactions/TransactionInvestigationModal";
import { InvestigationCase, TransactionRecord } from "@/types";
import { formatCurrency, getRiskColor, formatTimeAgo } from "@/lib/utils";
import { api } from "@/lib/api";
import {
  ShieldAlert,
  UserPlus,
  CheckCircle,
  Clock,
  AlertTriangle,
  MessageSquarePlus,
  ChevronLeft,
  ChevronRight,
  Eye,
  Send,
  CheckCircle2,
  XCircle,
} from "lucide-react";

export default function CasesPage() {
  const {
    cases,
    total,
    page,
    setPage,
    totalPages,
    statusFilter,
    setStatusFilter,
    isLoading,
    updateStatus,
    assignAnalyst,
  } = useCases();

  const [selectedCase, setSelectedCase] = useState<InvestigationCase | null>(null);
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [selectedAnalyst, setSelectedAnalyst] = useState("Sarah Chen");
  const [statusUpdateModal, setStatusUpdateModal] = useState(false);
  const [newStatus, setNewStatus] = useState("CONFIRMED_FRAUD");
  const [resolutionReason, setResolutionReason] = useState("Cardholder confirmed unauthorized activity.");
  const [caseNote, setCaseNote] = useState("");
  const [noteSuccess, setNoteSuccess] = useState<string | null>(null);

  // Investigation Modal
  const [investigationTx, setInvestigationTx] = useState<TransactionRecord | null>(null);
  const [isInvestigateOpen, setIsInvestigateOpen] = useState(false);

  const handleAssign = async () => {
    if (!selectedCase) return;
    await assignAnalyst(selectedCase.id, "USR_ANALYST_01", selectedAnalyst);
    setAssignModalOpen(false);
  };

  const handleStatusUpdate = async () => {
    if (!selectedCase) return;
    await updateStatus(selectedCase.id, newStatus, resolutionReason, caseNote || undefined);
    setStatusUpdateModal(false);
    setCaseNote("");
  };

  const handleAddNote = async () => {
    if (!selectedCase || !caseNote) return;
    try {
      await api.addCaseNote(selectedCase.id, caseNote);
      setNoteSuccess("Investigation note successfully appended to dossier.");
      setCaseNote("");
    } catch (e) {
      console.error("Failed to add note", e);
    }
  };

  const handleOpenTxModal = async (c: InvestigationCase) => {
    try {
      const res = await api.getTransactionDetail(c.transaction_id);
      if (res && res.transaction) {
        setInvestigationTx(res.transaction);
        setIsInvestigateOpen(true);
      }
    } catch {
      setInvestigationTx({
        transaction_id: c.transaction_id,
        card_id: c.card_id,
        cardholder_id: c.cardholder_id,
        amount: c.amount,
        currency: "USD",
        merchant_id: "M_SAMPLE",
        merchant_name: "Online Merchant",
        merchant_category: "ELECTRONICS",
        entry_mode: "CNP",
        risk_score: c.risk_score,
        risk_tier: c.severity,
        decision_action: "REVIEW",
        triggered_rules: ["RULE_AMT_003"],
        fraud_archetype: "ANOMALY",
        created_at: c.created_at,
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
            <ShieldAlert className="w-6 h-6 text-red-400" />
            <h1 className="text-2xl font-bold text-gray-100 tracking-tight">Case Management & Dispute Triage</h1>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Automated dispute defense queue with SLA tracking, evidence dossiers, and chargeback arbitration workflows.
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-2 flex-wrap">
          {["ALL", "OPEN", "IN_REVIEW", "CONFIRMED_FRAUD", "RESOLVED"].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st === "ALL" ? undefined : st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                (statusFilter === st || (st === "ALL" && !statusFilter))
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-500/20"
                  : "bg-gray-900 text-gray-400 hover:text-gray-200 border border-gray-800"
              }`}
            >
              {st.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>

      {/* Case Table Card */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-gray-300">
            <thead className="bg-gray-950/80 text-[11px] text-gray-400 uppercase tracking-wider border-b border-gray-800">
              <tr>
                <th className="py-3.5 px-4 font-semibold">Case #</th>
                <th className="py-3.5 px-4 font-semibold">Transaction / Masked Card</th>
                <th className="py-3.5 px-4 font-semibold">Amount</th>
                <th className="py-3.5 px-4 font-semibold">Risk Score</th>
                <th className="py-3.5 px-4 font-semibold">Severity</th>
                <th className="py-3.5 px-4 font-semibold">Status</th>
                <th className="py-3.5 px-4 font-semibold">Assigned Analyst</th>
                <th className="py-3.5 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {cases.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-gray-500">
                    No investigation cases found for selected filter.
                  </td>
                </tr>
              ) : (
                cases.map((c) => {
                  const riskColors = getRiskColor(c.severity);
                  const maskedCard = `**** **** **** ${c.card_id.slice(-4)}`;

                  return (
                    <tr key={c.id} className="hover:bg-gray-900/40 transition-colors">
                      <td className="py-3.5 px-4 font-mono font-bold text-blue-400">
                        {c.case_number}
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="font-mono text-gray-200 font-bold">{c.transaction_id}</div>
                        <div className="text-[10px] text-gray-500 font-mono">{maskedCard}</div>
                      </td>
                      <td className="py-3.5 px-4 font-bold text-gray-100">
                        {formatCurrency(c.amount)}
                      </td>
                      <td className="py-3.5 px-4 font-mono font-bold text-red-400">
                        {(c.risk_score * 100).toFixed(1)}%
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${riskColors.badge}`}>
                          {c.severity}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2.5 py-1 rounded text-[10px] font-bold ${
                          c.status === "CONFIRMED_FRAUD"
                            ? "bg-red-950 text-red-400 border border-red-800/40"
                            : c.status === "RESOLVED"
                            ? "bg-emerald-950 text-emerald-400 border border-emerald-800/40"
                            : "bg-blue-950 text-blue-400 border border-blue-800/40"
                        }`}>
                          {c.status.replace("_", " ")}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-medium text-gray-300">
                        {c.assigned_analyst_name || (
                          <span className="text-gray-500 italic">Unassigned</span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 text-right space-x-1.5">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleOpenTxModal(c)}
                          className="text-[11px]"
                        >
                          <Eye className="w-3 h-3 mr-1" />
                          Dossier
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedCase(c);
                            setAssignModalOpen(true);
                          }}
                          className="text-[11px]"
                        >
                          Assign
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => {
                            setSelectedCase(c);
                            setStatusUpdateModal(true);
                          }}
                          className="text-[11px]"
                        >
                          Action
                        </Button>
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
            Showing <strong className="text-gray-200">{(page - 1) * 20 + 1}</strong> to{" "}
            <strong className="text-gray-200">{Math.min(page * 20, total)}</strong> of{" "}
            <strong className="text-gray-200">{total}</strong> cases
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

      {/* Assign Analyst Modal */}
      <Modal
        isOpen={assignModalOpen}
        onClose={() => setAssignModalOpen(false)}
        title="Assign Investigation Case"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-xs text-gray-400">
            Assign case <strong className="text-gray-200">{selectedCase?.case_number}</strong> to a specialist.
          </p>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-gray-300">Fraud Specialist</label>
            <select
              value={selectedAnalyst}
              onChange={(e) => setSelectedAnalyst(e.target.value)}
              className="w-full bg-gray-900 border border-gray-800 rounded-lg p-2 text-xs text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="Sarah Chen">Sarah Chen (Lead Fraud Analyst)</option>
              <option value="Marcus Vance">Marcus Vance (Senior Specialist)</option>
              <option value="Elena Rostova">Elena Rostova (Risk Strategy Lead)</option>
            </select>
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-gray-800">
            <Button variant="secondary" size="sm" onClick={() => setAssignModalOpen(false)}>
              Cancel
            </Button>
            <Button size="sm" onClick={handleAssign}>
              Confirm Assignment
            </Button>
          </div>
        </div>
      </Modal>

      {/* Status Action Modal */}
      <Modal
        isOpen={statusUpdateModal}
        onClose={() => setStatusUpdateModal(false)}
        title={`Execute Action on Case ${selectedCase?.case_number}`}
        size="md"
      >
        <div className="space-y-4 text-xs">
          <div className="space-y-1.5">
            <label className="font-semibold text-gray-300">New Investigation Status</label>
            <select
              value={newStatus}
              onChange={(e) => setNewStatus(e.target.value)}
              className="w-full bg-gray-900 border border-gray-800 rounded-lg p-2 text-xs text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="CONFIRMED_FRAUD">CONFIRMED_FRAUD (Card Permanently Compromised)</option>
              <option value="RESOLVED">RESOLVED (False Positive / Genuine Customer)</option>
              <option value="IN_REVIEW">IN_REVIEW (Active Investigation Underway)</option>
              <option value="ESCALATED">ESCALATED (Forwarded to Senior Dispute Lead)</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="font-semibold text-gray-300">Resolution Reason</label>
            <input
              type="text"
              value={resolutionReason}
              onChange={(e) => setResolutionReason(e.target.value)}
              placeholder="e.g. Cardholder confirmed unauthorized ATM withdrawal"
              className="w-full bg-gray-900 border border-gray-800 rounded-lg p-2 text-xs text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          <div className="space-y-1.5">
            <label className="font-semibold text-gray-300">Investigation Note</label>
            <textarea
              value={caseNote}
              onChange={(e) => setCaseNote(e.target.value)}
              placeholder="Document evidence gathered, merchant contact, or telemetry findings..."
              className="w-full bg-gray-900 border border-gray-800 rounded-lg p-2 text-xs text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
              rows={3}
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-gray-800">
            <Button variant="secondary" size="sm" onClick={() => setStatusUpdateModal(false)}>
              Cancel
            </Button>
            <Button size="sm" onClick={handleStatusUpdate}>
              Submit Case Action
            </Button>
          </div>
        </div>
      </Modal>

      {/* Investigation Modal */}
      <TransactionInvestigationModal
        isOpen={isInvestigateOpen}
        onClose={() => setIsInvestigateOpen(false)}
        transaction={investigationTx}
        onActionComplete={useCases}
      />
    </div>
  );
}
