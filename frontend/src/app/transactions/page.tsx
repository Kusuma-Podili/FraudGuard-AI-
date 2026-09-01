"use client";

import React, { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { TransactionInvestigationModal } from "@/components/transactions/TransactionInvestigationModal";
import { api } from "@/lib/api";
import { TransactionRecord } from "@/types";
import { formatCurrency, getRiskColor, getActionBadge } from "@/lib/utils";
import {
  CreditCard,
  Search,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Download,
  FileSearch,
} from "lucide-react";

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<TransactionRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalPages, setTotalPages] = useState(1);
  const [isLoading, setIsLoading] = useState(false);

  // Filters
  const [search, setSearch] = useState("");
  const [riskLevel, setRiskLevel] = useState("ALL");
  const [decision, setDecision] = useState("ALL");
  const [category, setCategory] = useState("ALL");
  const [channel, setChannel] = useState("ALL");

  // Selected Transaction for Modal
  const [selectedTx, setSelectedTx] = useState<TransactionRecord | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchTransactions = async () => {
    setIsLoading(true);
    try {
      const res = await api.listTransactions({
        page,
        page_size: pageSize,
        search: search || undefined,
        risk_level: riskLevel !== "ALL" ? riskLevel : undefined,
        decision: decision !== "ALL" ? decision : undefined,
        category: category !== "ALL" ? category : undefined,
        channel: channel !== "ALL" ? channel : undefined,
      });
      setTransactions(res.items || []);
      setTotal(res.total || 0);
      setTotalPages(res.total_pages || 1);
    } catch (e) {
      console.error("Failed to load transactions", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [page, pageSize, riskLevel, decision, category, channel]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchTransactions();
  };

  const handleInvestigate = (tx: TransactionRecord) => {
    setSelectedTx(tx);
    setIsModalOpen(true);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <CreditCard className="w-6 h-6 text-[#5F8F83]" />
            <h1 className="text-2xl font-bold text-[#29332F] tracking-tight">Authorization Transactions</h1>
          </div>
          <p className="text-xs text-[#69736E] mt-1">
            Real-time ledger of all incoming payment authorizations with machine learning risk evaluation.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchTransactions} disabled={isLoading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <a href={api.getReportCsvDownloadUrl("TRANSACTIONS")} download>
            <Button size="sm" className="bg-[#5F8F83] hover:bg-[#4F7D72] text-white shadow-sm">
              <Download className="w-3.5 h-3.5 mr-1" />
              Download CSV
            </Button>
          </a>
        </div>
      </div>

      {/* Filter Control Bar */}
      <Card className="p-4 bg-[#FFFDFC] border-[#E5DED5]">
        <form onSubmit={handleSearchSubmit} className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[220px]">
            <Search className="w-4 h-4 text-[#929A95] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by card number (e.g. 4829), Tx ID, merchant, country..."
              className="w-full bg-[#F7F4EF] border border-[#E5DED5] rounded-lg pl-9 pr-3 py-1.5 text-xs text-[#29332F] placeholder-[#929A95] focus:outline-none focus:ring-1 focus:ring-[#5F8F83]"
            />
          </div>

          <select
            value={riskLevel}
            onChange={(e) => {
              setRiskLevel(e.target.value);
              setPage(1);
            }}
            className="bg-[#F7F4EF] border border-[#E5DED5] rounded-lg px-3 py-1.5 text-xs text-[#29332F] focus:outline-none focus:ring-1 focus:ring-[#5F8F83]"
          >
            <option value="ALL">All Risk Tiers</option>
            <option value="LOW">Low Risk (&lt;0.30)</option>
            <option value="MEDIUM">Medium Risk (0.30–0.60)</option>
            <option value="HIGH">High Risk (0.60–0.80)</option>
            <option value="CRITICAL">Critical Risk (&gt;0.80)</option>
          </select>

          <select
            value={decision}
            onChange={(e) => {
              setDecision(e.target.value);
              setPage(1);
            }}
            className="bg-[#F7F4EF] border border-[#E5DED5] rounded-lg px-3 py-1.5 text-xs text-[#29332F] focus:outline-none focus:ring-1 focus:ring-[#5F8F83]"
          >
            <option value="ALL">All Decisions</option>
            <option value="ALLOW">ALLOW (Approved)</option>
            <option value="REVIEW">REVIEW (Manual Triage)</option>
            <option value="CHALLENGE_3DS">CHALLENGE_3DS</option>
            <option value="DECLINE">DECLINE (Blocked)</option>
          </select>

          <Button type="submit" size="sm">
            Search
          </Button>
        </form>
      </Card>

      {/* Main Transactions Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-[#29332F]">
            <thead className="bg-[#F7F4EF] text-[11px] text-[#69736E] uppercase tracking-wider border-b border-[#E5DED5]">
              <tr>
                <th className="py-3.5 px-4 font-semibold">Tx ID</th>
                <th className="py-3.5 px-4 font-semibold">Masked Card</th>
                <th className="py-3.5 px-4 font-semibold">Timestamp</th>
                <th className="py-3.5 px-4 font-semibold">Amount</th>
                <th className="py-3.5 px-4 font-semibold">Merchant / Category</th>
                <th className="py-3.5 px-4 font-semibold">Channel</th>
                <th className="py-3.5 px-4 font-semibold">Risk Score</th>
                <th className="py-3.5 px-4 font-semibold">Decision</th>
                <th className="py-3.5 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E5DED5]/60">
              {transactions.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-[#929A95]">
                    No transactions found matching the specified filters.
                  </td>
                </tr>
              ) : (
                transactions.map((tx) => {
                  const riskColors = getRiskColor(tx.risk_tier);
                  const decisionBadge = getActionBadge(tx.decision_action);
                  const maskedCard = `**** **** **** ${tx.card_id.slice(-4)}`;

                  return (
                    <tr key={tx.transaction_id} className="hover:bg-[#F7F4EF] transition-colors">
                      <td className="py-3.5 px-4 font-mono font-bold text-[#29332F]">
                        {tx.transaction_id}
                      </td>
                      <td className="py-3.5 px-4 font-mono text-[#69736E]">
                        {maskedCard}
                      </td>
                      <td className="py-3.5 px-4 text-[#929A95] font-mono text-[11px]">
                        {new Date(tx.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                      </td>
                      <td className="py-3.5 px-4 font-bold text-[#29332F]">
                        {formatCurrency(tx.amount)}
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-[#29332F]">{tx.merchant_name || tx.merchant_id}</div>
                        <div className="text-[10px] text-[#929A95]">
                          {tx.merchant_category} • {tx.country_code || "US"}
                        </div>
                      </td>
                      <td className="py-3.5 px-4 font-mono text-[11px] text-[#69736E]">
                        {tx.entry_mode || "CNP"}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${riskColors.badge}`}>
                          {(tx.risk_score * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${decisionBadge.className}`}>
                          {decisionBadge.label}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleInvestigate(tx)}
                          className="text-[11px]"
                        >
                          <FileSearch className="w-3 h-3 mr-1 text-[#5F8F83]" />
                          Investigate
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
            Showing <strong className="text-[#29332F]">{(page - 1) * pageSize + 1}</strong> to{" "}
            <strong className="text-[#29332F]">{Math.min(page * pageSize, total)}</strong> of{" "}
            <strong className="text-[#29332F]">{total}</strong> records
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

      {/* Investigation Dossier Modal */}
      <TransactionInvestigationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        transaction={selectedTx}
        onActionComplete={fetchTransactions}
      />
    </div>
  );
}
