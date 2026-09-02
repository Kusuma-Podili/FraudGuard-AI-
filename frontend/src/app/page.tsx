"use client";

import React, { useState, useEffect } from "react";
import { MetricCard } from "@/components/ui/MetricCard";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { RiskTrendChart } from "@/components/charts/RiskTrendChart";
import { RocCurveChart } from "@/components/charts/RocCurveChart";
import { TransactionInvestigationModal } from "@/components/transactions/TransactionInvestigationModal";
import { useAnalytics } from "@/hooks/useAnalytics";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import { TransactionRecord, FraudAlert, InvestigationCase } from "@/types";
import { formatCurrency, getRiskColor, getActionBadge } from "@/lib/utils";
import Link from "next/link";
import {
  ShieldAlert,
  IndianRupee,
  TrendingDown,
  Bell,
  Radio,
  ArrowRight,
  FileSearch,
  Zap,
} from "lucide-react";

export default function DashboardPage() {
  const { kpis, hourlyTrends, isLoading } = useAnalytics();
  const { user, isAdmin } = useAuth();
  const [recentTransactions, setRecentTransactions] = useState<TransactionRecord[]>([]);
  const [recentAlerts, setRecentAlerts] = useState<FraudAlert[]>([]);
  const [openCases, setOpenCases] = useState<InvestigationCase[]>([]);
  const [selectedTx, setSelectedTx] = useState<TransactionRecord | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        const [txRes, altRes, caseRes] = await Promise.all([
          api.listTransactions({ page: 1, page_size: 6 }),
          api.listAlerts({ page: 1, page_size: 5, status: "NEW" }),
          api.listCases({ page: 1, page_size: 5, status: "OPEN" }),
        ]);
        setRecentTransactions(txRes.items || []);
        setRecentAlerts(altRes.items || []);
        setOpenCases(caseRes.items || []);
      } catch (e) {
        console.error("Failed to load dashboard data", e);
      }
    }
    loadData();
  }, []);

  const handleInvestigate = (tx: TransactionRecord) => {
    setSelectedTx(tx);
    setIsModalOpen(true);
  };

  const sampleRoc = [
    { fpr: 0.0, tpr: 0.0 },
    { fpr: 0.01, tpr: 0.78 },
    { fpr: 0.02, tpr: 0.89 },
    { fpr: 0.05, tpr: 0.94 },
    { fpr: 0.1, tpr: 0.98 },
    { fpr: 0.2, tpr: 0.99 },
    { fpr: 1.0, tpr: 1.0 },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#111827] tracking-tight">
            {isAdmin ? "Executive Defense Overview" : "Analyst Triage & Threat Queue"}
          </h1>
          <p className="text-xs text-[#4B5563] mt-1">
            {isAdmin
              ? "Real-time telemetry, rupee savings, and machine learning gateway health."
              : `Welcome back, ${user?.full_name || "Analyst"}. Prioritized high-risk authorizations requiring operational review.`}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/live-monitor">
            <Button size="sm" className="bg-[#FB923C] hover:bg-[#F97316] text-white shadow-sm flex items-center gap-2">
              <Radio className="w-3.5 h-3.5" />
              <span>Live Threat Radar</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title={isAdmin ? "Total Fraud Prevented" : "My Assigned Cases"}
          value={
            isAdmin
              ? kpis ? formatCurrency(kpis.fraud_prevented_usd) : "₹1,84,200.00"
              : `${openCases.length} Pending`
          }
          change={isAdmin ? "+14.2% rupee savings" : "2 Critical SLA"}
          isPositive={true}
          icon={isAdmin ? <span className="font-bold text-base">₹</span> : <ShieldAlert className="w-5 h-5 text-[#EA580C]" />}
        />
        <MetricCard
          title={isAdmin ? "Global Fraud Rate" : "High-Risk Queue"}
          value={isAdmin ? `${(kpis?.fraud_rate_pct || 0.42).toFixed(2)}%` : "14 Flags"}
          change={isAdmin ? "-0.18% reduction" : "+3 in last hour"}
          isPositive={true}
          icon={<TrendingDown className="w-5 h-5 text-gray-700" />}
        />
        <MetricCard
          title={isAdmin ? "Active Alerts" : "Unresolved Alerts"}
          value={kpis ? kpis.active_alerts_count : recentAlerts.length}
          subtitle={isAdmin ? "Across all payment rails" : "Requiring investigation"}
          icon={<Bell className="w-5 h-5 text-[#EA580C]" />}
        />
        <MetricCard
          title="P99 SLA Latency"
          value={kpis ? `${kpis.p99_inference_latency_ms.toFixed(1)}ms` : "14.2ms"}
          subtitle="Sub-20ms SLA Guarantee"
          isPositive={true}
          icon={<Zap className="w-5 h-5 text-gray-700" />}
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div>
                <CardTitle>24-Hour Fraud Velocity & Volume</CardTitle>
                <CardDescription>
                  Continuous time-series tracking of total authorized volume vs intercepted fraudulent transactions.
                </CardDescription>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded bg-gray-100 text-gray-700 font-mono font-semibold">
                Rolling 24h
              </span>
            </CardHeader>
            <RiskTrendChart data={hourlyTrends} />
          </Card>
        </div>

        <div>
          <Card>
            <CardHeader>
              <div>
                <CardTitle>ML Model ROC Discrimination</CardTitle>
                <CardDescription>ROC-AUC curve (0.988) across classification thresholds.</CardDescription>
              </div>
            </CardHeader>
            <RocCurveChart data={sampleRoc} />
          </Card>
        </div>
      </div>

      {/* Bottom Section */}
      {isAdmin ? (
        /* Admin View: Recent Transactions */
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between w-full">
              <div>
                <CardTitle>Recent High-Risk Authorizations</CardTitle>
                <CardDescription>
                  Real-time incoming transaction ledger evaluated by dynamic rules and gradient boosting models.
                </CardDescription>
              </div>
              <Link href="/transactions">
                <Button variant="ghost" size="sm" className="text-xs font-semibold text-[#EA580C]">
                  <span>View All Ledger</span>
                  <ArrowRight className="w-3.5 h-3.5 ml-1" />
                </Button>
              </Link>
            </div>
          </CardHeader>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-[#111827]">
              <thead className="bg-[#F9FAFB] text-[11px] text-[#4B5563] uppercase tracking-wider border-b border-[#E5E7EB]">
                <tr>
                  <th className="py-3 px-4 font-semibold">Tx ID</th>
                  <th className="py-3 px-4 font-semibold">Masked Card</th>
                  <th className="py-3 px-4 font-semibold">Amount</th>
                  <th className="py-3 px-4 font-semibold">Merchant / Category</th>
                  <th className="py-3 px-4 font-semibold">Channel</th>
                  <th className="py-3 px-4 font-semibold">Risk Score</th>
                  <th className="py-3 px-4 font-semibold">Decision</th>
                  <th className="py-3 px-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E5E7EB]">
                {recentTransactions.map((tx) => {
                  const riskColors = getRiskColor(tx.risk_tier);
                  const decisionBadge = getActionBadge(tx.decision_action);
                  const maskedCard = `**** **** **** ${tx.card_id.slice(-4)}`;

                  return (
                    <tr key={tx.transaction_id} className="hover:bg-gray-50 transition-colors">
                      <td className="py-3.5 px-4 font-mono font-bold text-[#111827]">{tx.transaction_id}</td>
                      <td className="py-3.5 px-4 font-mono text-[#4B5563]">{maskedCard}</td>
                      <td className="py-3.5 px-4 font-bold text-[#111827]">{formatCurrency(tx.amount)}</td>
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-[#111827]">{tx.merchant_name || tx.merchant_id}</div>
                        <div className="text-[10px] text-[#9CA3AF]">{tx.merchant_category} • {tx.country_code || "IN"}</div>
                      </td>
                      <td className="py-3.5 px-4 font-mono text-[11px] text-[#4B5563]">{tx.entry_mode || "CNP"}</td>
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
                          <FileSearch className="w-3 h-3 mr-1 text-gray-700" />
                          Dossier
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      ) : (
        /* Analyst View: Prioritized Queue & Open Cases */
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Active Alerts Queue */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-2">
                  <Bell className="w-4 h-4 text-[#EA580C]" />
                  <CardTitle>High-Priority Alert Triage</CardTitle>
                </div>
                <Link href="/alerts" className="text-xs text-[#EA580C] font-semibold hover:underline">
                  All Alerts
                </Link>
              </div>
            </CardHeader>

            <div className="divide-y divide-[#E5E7EB]">
              {recentAlerts.map((alt) => (
                <div key={alt.alert_id} className="p-3.5 flex items-center justify-between hover:bg-gray-50 rounded-xl transition-colors">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-xs text-[#111827]">{alt.alert_id}</span>
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-[#FFEDD5] text-[#9A3412] border border-[#FDBA74]">
                        {alt.severity}
                      </span>
                    </div>
                    <p className="text-xs text-[#111827]">{alt.reason}</p>
                    <span className="text-[10px] text-[#9CA3AF]">{alt.created_at}</span>
                  </div>
                  <Link href="/alerts">
                    <Button variant="secondary" size="sm" className="text-xs">
                      Triage
                    </Button>
                  </Link>
                </div>
              ))}
            </div>
          </Card>

          {/* Assigned Cases */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-[#EA580C]" />
                  <CardTitle>My Open Investigation Cases</CardTitle>
                </div>
                <Link href="/cases" className="text-xs text-[#EA580C] font-semibold hover:underline">
                  Case Ledger
                </Link>
              </div>
            </CardHeader>

            <div className="divide-y divide-[#E5E7EB]">
              {openCases.map((c) => (
                <div key={c.id} className="p-3.5 flex items-center justify-between hover:bg-gray-50 rounded-xl transition-colors">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-xs text-[#111827]">{c.case_number}</span>
                      <span className="font-bold text-xs text-[#111827]">{formatCurrency(c.amount)}</span>
                    </div>
                    <p className="text-xs text-[#4B5563]">Tx: {c.transaction_id} • Card **** {c.card_id.slice(-4)}</p>
                    <span className="text-[10px] text-gray-600 font-semibold">Status: {c.status}</span>
                  </div>
                  <Link href="/cases">
                    <Button variant="secondary" size="sm" className="text-xs">
                      Open Case
                    </Button>
                  </Link>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {/* Investigation Dossier Modal */}
      <TransactionInvestigationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        transaction={selectedTx}
        onActionComplete={() => {
          setIsModalOpen(false);
        }}
      />
    </div>
  );
}
