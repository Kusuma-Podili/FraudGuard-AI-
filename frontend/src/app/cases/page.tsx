"use client";

import React, { useState } from "react";
import { useCases } from "@/hooks/useCases";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Select } from "@/components/ui/Select";
import { InvestigationCase } from "@/types";
import { formatCurrency, getRiskColor, formatTimeAgo } from "@/lib/utils";
import { ShieldAlert, UserPlus, CheckCircle, Clock, AlertTriangle, MessageSquarePlus } from "lucide-react";

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
  const [selectedAnalyst, setSelectedAnalyst] = useState("Jane Doe");
  const [statusUpdateModal, setStatusUpdateModal] = useState(false);
  const [newStatus, setNewStatus] = useState("CONFIRMED_FRAUD");
  const [resolutionReason, setResolutionReason] = useState("Cardholder confirmed unauthorized activity.");

  const handleAssign = async () => {
    if (!selectedCase) return;
    await assignAnalyst(selectedCase.id, "USR_ANALYST_02", selectedAnalyst);
    setAssignModalOpen(false);
  };

  const handleStatusUpdate = async () => {
    if (!selectedCase) return;
    await updateStatus(selectedCase.id, newStatus, resolutionReason);
    setStatusUpdateModal(false);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-100 tracking-tight">Case Management & Triage</h1>
          <p className="text-xs text-gray-400 mt-1">
            Automated triage queue with SLA tracking, evidence dossiers, and chargeback defense workflows.
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-2">
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
                <th className="py-3.5 px-4 font-semibold">Transaction / Card</th>
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
                  <td colSpan={8} className="py-8 text-center text-gray-500">
                    No open cases found for selected filter.
                  </td>
                </tr>
              ) : (
                cases.map((c) => {
                  const riskColors = getRiskColor(c.severity);

                  return (
                    <tr key={c.id} className="hover:bg-gray-800/40 transition-colors">
                      <td className="py-3 px-4 font-mono font-bold text-blue-400">
                        {c.case_number}
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-mono text-gray-200">{c.transaction_id}</div>
                        <div className="text-[10px] text-gray-500">{c.card_id}</div>
                      </td>
                      <td className="py-3 px-4 font-semibold text-gray-100">
                        {formatCurrency(c.amount)}
                      </td>
                      <td className="py-3 px-4 font-mono font-bold text-red-400">
                        {(c.risk_score * 100).toFixed(1)}%
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${riskColors.badge}`}>
                          {c.severity}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-gray-800 text-gray-300 border border-gray-700">
                          {c.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-300 text-xs">
                        {c.assigned_analyst_name || <span className="text-gray-500 italic">Unassigned</span>}
                      </td>
                      <td className="py-3 px-4 text-right space-x-2">
                        <button
                          onClick={() => {
                            setSelectedCase(c);
                            setAssignModalOpen(true);
                          }}
                          className="p-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white transition-colors"
                          title="Assign Analyst"
                        >
                          <UserPlus className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => {
                            setSelectedCase(c);
                            setStatusUpdateModal(true);
                          }}
                          className="p-1.5 rounded-lg bg-blue-600/20 hover:bg-blue-600 text-blue-400 hover:text-white transition-colors"
                          title="Transition Status"
                        >
                          <CheckCircle className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Assign Analyst Modal */}
      <Modal
        isOpen={assignModalOpen}
        onClose={() => setAssignModalOpen(false)}
        title={`Assign Case: ${selectedCase?.case_number}`}
        maxWidth="md"
      >
        <div className="space-y-4">
          <Select
            label="Select Lead Fraud Analyst"
            value={selectedAnalyst}
            onChange={(e) => setSelectedAnalyst(e.target.value)}
            options={[
              { value: "Jane Doe", label: "Jane Doe (Senior Analyst)" },
              { value: "Alex Smith", label: "Alex Smith (Tier 2 Triage)" },
              { value: "Marcus Brody", label: "Marcus Brody (Organized Crime Lead)" },
            ]}
          />
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => setAssignModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleAssign}>
              Confirm Assignment
            </Button>
          </div>
        </div>
      </Modal>

      {/* Status Transition Modal */}
      <Modal
        isOpen={statusUpdateModal}
        onClose={() => setStatusUpdateModal(false)}
        title={`Transition Case Status: ${selectedCase?.case_number}`}
        maxWidth="md"
      >
        <div className="space-y-4">
          <Select
            label="New Case Disposition"
            value={newStatus}
            onChange={(e) => setNewStatus(e.target.value)}
            options={[
              { value: "CONFIRMED_FRAUD", label: "CONFIRMED_FRAUD (Card Compromised)" },
              { value: "FALSE_POSITIVE", label: "FALSE_POSITIVE (Customer Authorized)" },
              { value: "CHARGEBACK_FILED", label: "CHARGEBACK_FILED (Dispute Submitted)" },
              { value: "RESOLVED", label: "RESOLVED (Case Closed)" },
            ]}
          />
          <div>
            <label className="block text-xs font-medium text-gray-300 mb-1.5">Resolution Notes</label>
            <textarea
              rows={3}
              value={resolutionReason}
              onChange={(e) => setResolutionReason(e.target.value)}
              className="w-full bg-gray-950 border border-gray-800 rounded-lg p-2.5 text-xs text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => setStatusUpdateModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleStatusUpdate}>
              Submit Disposition
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
