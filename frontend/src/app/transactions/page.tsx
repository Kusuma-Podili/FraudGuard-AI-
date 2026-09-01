"use client";

import React, { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { TransactionTable } from "@/components/transactions/TransactionTable";
import { TransactionInvestigationModal } from "@/components/transactions/TransactionInvestigationModal";
import { api } from "@/lib/api";
import { TransactionRecord } from "@/types";
import { formatCurrency, getRiskColor, getActionBadge } from "@/lib/utils";
import {
  CreditCard,
  Search,
  Filter,
  RefreshCw,
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  ArrowUpDown,
  Download,
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
            <CreditCard className="w-6 h-6 text-blue-400" />
            <h1 className="text-2xl font-bold text-gray-100 tracking-tight">Authorization Transactions</h1>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Real-time ledger of all incoming payment authorizations with machine learning risk evaluation.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchTransactions} disabled={isLoading}>
            <RefreshCw className={`w-3.5 h-3.5 mr-1 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <a href={api.getReportCsvDownloadUrl("TRANSACTIONS")} download>
            <Button variant="secondary" size="sm">
              <Download className="w-3.5 h-3.5 mr-1" />
              Export CSV
            </Button>
          </a>
        </div>
      </div>

      {/* Filter Control Card */}
      <Card className="p-4 space-y-3 bg-gray-950/60 border-gray-800">
        <form onSubmit={handleSearchSubmit} className="flex flex-wrap items-center gap-3">
          {/* Search Box */}
          <div className="relative flex-1 min-w-[240px]">
            <Search className="w-4 h-4 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by Tx ID, Card ID, Merchant, or Country..."
              className="w-full bg-gray-900 border border-gray-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>

          {/* Risk Level Filter */}
          <select
            value={riskLevel}
            onChange={(e) => {
              setRiskLevel(e.target.value);
              setPage(1);
            }}
            className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-xs text-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="ALL">All Risk Tiers</option>
            <option value="LOW">Low Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="HIGH">High Risk</option>
            <option value="CRITICAL">Critical Risk</option>
          </select>

          {/* Decision Filter */}
          <select
            value={decision}
            onChange={(e) => {
              setDecision(e.target.value);
              setPage(1);
            }}
            className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-xs text-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="ALL">All Decisions</option>
            <option value="ALLOW">ALLOW (Approved)</option>
            <option value="REVIEW">REVIEW (Flagged)</option>
            <option value="CHALLENGE_3DS">CHALLENGE_3DS</option>
            <option value="DECLINE">DECLINE (Blocked)</option>
          </select>

          {/* Category Filter */}
          <select
            value={category}
            onChange={(e) => {
              setCategory(e.target.value);
              setPage(1);
            }}
            className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-xs text-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="ALL">All Categories</option>
            <option value="ELECTRONICS">Electronics</option>
            <option value="CRYPTO_EXCHANGE">Crypto Exchange</option>
            <option value="LUXURY_JEWELRY">Luxury Jewelry</option>
            <option value="TRAVEL_AIRLINE">Travel & Airline</option>
            <option value="E_COMMERCE">E-Commerce</option>
            <option value="GROCERY">Grocery</option>
            <option value="GAMBLING">Gambling</option>
          </select>

          {/* Channel Filter */}
          <select
            value={channel}
            onChange={(e) => {
              setChannel(e.target.value);
              setPage(1);
            }}
            className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5 text-xs text-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="ALL">All Channels</option>
            <option value="CNP">CNP Web / Online</option>
            <option value="POS_CHIP">POS EMV Chip</option>
            <option value="POS_CONTACTLESS">POS Contactless</option>
            <option value="ATM">ATM Withdrawal</option>
          </select>

          <Button type="submit" size="sm">
            Apply Filters
          </Button>
        </form>
      </Card>

      {/* Main Transactions Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-gray-300">
            <thead className="bg-gray-950/80 text-[11px] text-gray-400 uppercase tracking-wider border-b border-gray-800">
              <tr>
                <th className="py-3.5 px-4 font-semibold">Tx ID</th>
                <th className="py-3.5 px-4 font-semibold">Masked Card</th>
                <th className="py-3.5 px-4 font-semibold">Amount</th>
                <th className="py-3.5 px-4 font-semibold">Merchant / Category</th>
                <th className="py-3.5 px-4 font-semibold">Channel</th>
                <th className="py-3.5 px-4 font-semibold">Risk Score</th>
                <th className="py-3.5 px-4 font-semibold">Decision</th>
                <th className="py-3.5 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {transactions.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-gray-500">
                    No transactions match current filters.
                  </td>
                </tr>
              ) : (
                transactions.map((tx) => {
                  const riskTier = tx.risk_tier || (tx.risk_score >= 0.8 ? "CRITICAL" : tx.risk_score >= 0.6 ? "HIGH" : tx.risk_score >= 0.3 ? "MEDIUM" : "LOW");
                  const riskBadge = getRiskColor(riskTier);
                  const actionBadge = getActionBadge(tx.decision_action);
                  const maskedCard = `**** **** **** ${tx.card_id.slice(-4)}`;

                  return (
                    <tr key={tx.transaction_id} className="hover:bg-gray-900/40 transition-colors group">
                      <td className="py-3 px-4 font-mono font-bold text-gray-200">
                        {tx.transaction_id}
                      </td>
                      <td className="py-3 px-4 font-mono text-gray-300">
                        {maskedCard}
                      </td>
                      <td className="py-3 px-4 font-bold text-gray-100">
                        {formatCurrency(tx.amount)}
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-semibold text-gray-200">{tx.merchant_name || tx.merchant_id}</div>
                        <div className="text-[10px] text-gray-500">{tx.merchant_category} • {tx.country_code || "US"}</div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-300 font-mono text-[10px]">
                          {tx.entry_mode || "CNP"}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 rounded text-[11px] font-bold border ${riskBadge.bg} ${riskBadge.text} ${riskBadge.border}`}>
                            {tx.risk_score.toFixed(2)}
                          </span>
                          <span className="text-[10px] text-gray-500">{riskTier}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2.5 py-1 rounded text-[11px] font-bold ${actionBadge.color}`}>
                          {tx.decision_action}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleInvestigate(tx)}
                          className="text-[11px]"
                        >
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
        <div className="p-4 border-t border-gray-800 flex items-center justify-between text-xs text-gray-400">
          <div>
            Showing <strong className="text-gray-200">{(page - 1) * pageSize + 1}</strong> to{" "}
            <strong className="text-gray-200">{Math.min(page * pageSize, total)}</strong> of{" "}
            <strong className="text-gray-200">{total}</strong> transactions
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
