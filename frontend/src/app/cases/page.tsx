"use client";

import React, { useState } from "react";
import { useCases } from "@/hooks/useCases";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { TransactionInvestigationModal } from "@/components/transactions/TransactionInvestigationModal";
import { InvestigationCase, TransactionRecord } from "@/types";
import { formatCurrency, getRiskColor } from "@/lib/utils";
import { api } from "@/lib/api";
import {
  ShieldAlert,
  ChevronLeft,
  ChevronRight,
  Eye,
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
            <ShieldAlert className="w-6 h-6 text-[#5F8F83]" />
            <h1 className="text-2xl font-bold text-[#29332F] tracking-tight">Case Management & Dispute Triage</h1>
          </div>
          <p className="text-xs text-[#69736E] mt-1">
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
                  ? "bg-[#5F8F83] text-white shadow-sm"
                  : "bg-[#FFFDFC] text-[#69736E] hover:text-[#29332F] border border-[#E5DED5]"
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
          <table className="w-full text-left text-xs text-[#29332F]">
            <thead className="bg-[#F7F4EF] text-[11px] text-[#69736E] uppercase tracking-wider border-b border-[#E5DED5]">
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
            <tbody className="divide-y divide-[#E5DED5]/60">
              {cases.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-[#929A95]">
                    No investigation cases found for selected filter.
                  </td>
                </tr>
              ) : (
                cases.map((c) => {
                  const riskColors = getRiskColor(c.severity);
                  const maskedCard = `**** **** **** ${c.card_id.slice(-4)}`;

                  return (
                    <tr key={c.id} className="hover:bg-[#F7F4EF] transition-colors">
                      <td className="py-3.5 px-4 font-mono font-bold text-[#5F8F83]">
                        {c.case_number}
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="font-mono text-[#29332F] font-bold">{c.transaction_id}</div>
                        <div className="text-[10px] text-[#69736E] font-mono">{maskedCard}</div>
                      </td>
                      <td className="py-3.5 px-4 font-bold text-[#29332F]">
                        {formatCurrency(c.amount)}
                      </td>
                      <td className="py-3.5 px-4 font-mono font-bold text-[#7B3030]">
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
                            ? "bg-[#D99A9A]/30 text-[#7B3030] border border-[#D99A9A]"
                            : c.status === "RESOLVED"
                            ? "bg-[#A8C5B5]/30 text-[#35604B] border border-[#A8C5B5]"
                            : "bg-[#DCE7E1] text-[#26332F] border border-[#CCD9D2]"
                        }`}>
                          {c.status.replace("_", " ")}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-medium text-[#69736E]">
                        {c.assigned_analyst_name || (
                          <span className="text-[#929A95] italic">Unassigned</span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 text-right space-x-1.5">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleOpenTxModal(c)}
                          className="text-[11px]"
                        >
                          <Eye className="w-3 h-3 mr-1 text-[#5F8F83]" />
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
        <div className="p-4 border-t border-[#E5DED5] flex items-center justify-between text-xs text-[#69736E]">
          <div>
            Showing <strong className="text-[#29332F]">{(page - 1) * 20 + 1}</strong> to{" "}
            <strong className="text-[#29332F]">{Math.min(page * 20, total)}</strong> of{" "}
            <strong className="text-[#29332F]">{total}</strong> cases
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

      {/* Assign Analyst Modal */}
      <Modal
        isOpen={assignModalOpen}
        onClose={() => setAssignModalOpen(false)}
        title="Assign Investigation Case"
        size="sm"
      >
        <div className="space-y-4">
          <p className="text-xs text-[#69736E]">
            Assign case <strong className="text-[#29332F]">{selectedCase?.case_number}</strong> to a specialist.
          </p>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-[#29332F]">Fraud Specialist</label>
            <select
              value={selectedAnalyst}
              onChange={(e) => setSelectedAnalyst(e.target.value)}
              className="w-full bg-[#F7F4EF] border border-[#E5DED5] rounded-lg p-2 text-xs text-[#29332F] focus:outline-none focus:ring-1 focus:ring-[#5F8F83]"
            >
              <option value="Sarah Chen">Sarah Chen (Lead Fraud Analyst)</option>
              <option value="Marcus Vance">Marcus Vance (Senior Specialist)</option>
              <option value="Elena Rostova">Elena Rostova (Risk Strategy Lead)</option>
            </select>
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-[#E5DED5]">
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
            <label className="font-semibold text-[#29332F]">New Investigation Status</label>
            <select
              value={newStatus}
              onChange={(e) => setNewStatus(e.target.value)}
              className="w-full bg-[#F7F4EF] border border-[#E5DED5] rounded-lg p-2 text-xs text-[#29332F] focus:outline-none focus:ring-1 focus:ring-[#5F8F83]"
            >
              <option value="CONFIRMED_FRAUD">CONFIRMED_FRAUD (Card Permanently Compromised)</option>
              <option value="RESOLVED">RESOLVED (False Positive / Genuine Customer)</option>
              <option value="IN_REVIEW">IN_REVIEW (Active Investigation Underway)</option>
              <option value="ESCALATED">ESCALATED (Forwarded to Senior Dispute Lead)</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="font-semibold text-[#29332F]">Resolution Reason</label>
            <input
              type="text"
              value={resolutionReason}
              onChange={(e) => setResolutionReason(e.target.value)}
              placeholder="e.g. Cardholder confirmed unauthorized ATM withdrawal"
              className="w-full bg-[#F7F4EF] border border-[#E5DED5] rounded-lg p-2 text-xs text-[#29332F] focus:outline-none focus:ring-1 focus:ring-[#5F8F83]"
            />
          </div>

          <div className="space-y-1.5">
            <label className="font-semibold text-[#29332F]">Investigation Note</label>
            <textarea
              value={caseNote}
              onChange={(e) => setCaseNote(e.target.value)}
              placeholder="Document evidence gathered, merchant contact, or telemetry findings..."
              className="w-full bg-[#F7F4EF] border border-[#E5DED5] rounded-lg p-2 text-xs text-[#29332F] focus:outline-none focus:ring-1 focus:ring-[#5F8F83]"
              rows={3}
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-[#E5DED5]">
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
