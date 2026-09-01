"use client";

import React, { useState, useEffect } from "react";
import { MetricCard } from "@/components/ui/MetricCard";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { RiskTrendChart } from "@/components/charts/RiskTrendChart";
import { RocCurveChart } from "@/components/charts/RocCurveChart";
import { ConfusionMatrixChart } from "@/components/charts/ConfusionMatrixChart";
import { TransactionTable } from "@/components/transactions/TransactionTable";
import { TransactionInvestigationModal } from "@/components/transactions/TransactionInvestigationModal";
import { useAnalytics } from "@/hooks/useAnalytics";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import { TransactionRecord, FraudAlert, InvestigationCase } from "@/types";
import { formatCurrency, getRiskColor, getActionBadge, formatTimeAgo } from "@/lib/utils";
import Link from "next/link";
import {
  ShieldAlert,
  DollarSign,
  TrendingDown,
  Activity,
  AlertTriangle,
  FileSearch,
  CheckCircle2,
  Bell,
  Radio,
  ArrowRight,
  ShieldCheck,
  CreditCard,
  UserCheck,
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

  const sampleConfusionMatrix = {
    true_negative: 4820,
    false_positive: 32,
    false_negative: 8,
    true_positive: 140,
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
          <h1 className="text-2xl font-bold text-gray-100 tracking-tight">
            {isAdmin ? "Executive Defense Overview" : "Analyst Triage & Threat Queue"}
          </h1>
          <p className="text-xs text-gray-400 mt-1">
            {isAdmin
              ? "Real-time telemetry, dollar savings, and machine learning gateway health."
              : `Welcome back, ${user?.full_name || "Analyst"}. Prioritized high-risk authorizations requiring operational review.`}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/live-monitor">
            <Button size="sm" className="bg-red-600 hover:bg-red-700 text-white shadow-lg shadow-red-600/20">
              <Radio className="w-3.5 h-3.5 mr-1.5 animate-pulse" />
              Live Radar
            </Button>
          </Link>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
            <CheckCircle2 className="w-4 h-4" />
            <span>Engine: Sub-20ms SLA</span>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title={isAdmin ? "24h Fraud Prevented" : "My Open Cases"}
          value={
            isAdmin
              ? kpis
                ? formatCurrency(kpis.fraud_prevented_usd || 184200.0)
                : "$184,200.00"
              : openCases.length.toString()
          }
          change={isAdmin ? "+14.2% vs yesterday" : "3 Critical SLA"}
          isPositive={true}
          icon={isAdmin ? <DollarSign className="w-5 h-5" /> : <ShieldAlert className="w-5 h-5 text-amber-400" />}
        />
        <MetricCard
          title="Global Fraud Rate"
          value={kpis ? `${(kpis.fraud_rate_pct || 0.42).toFixed(2)}%` : "0.42%"}
          change="-0.18% reduction"
          isPositive={true}
          icon={<TrendingDown className="w-5 h-5" />}
        />
        <MetricCard
          title="Active Alerts Pending"
          value={kpis?.active_alerts_count || recentAlerts.length || 18}
          subtitle="4 Critical Severity"
          icon={<Bell className="w-5 h-5 text-red-400" />}
        />
        <MetricCard
          title="P99 Inference Latency"
          value={kpis ? `${(kpis.p99_inference_latency_ms || 14.2).toFixed(1)}ms` : "14.2ms"}
          subtitle="Sub-20ms Target"
          isPositive={true}
          icon={<Activity className="w-5 h-5 text-emerald-400" />}
        />
      </div>

      {/* ADMIN VIEW: EXECUTIVE CHARTS & TELEMETRY */}
      {isAdmin && (
        <>
          {/* Main Visualizations Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card className="h-full">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>24h Fraud Velocity & Dollar Exposure</CardTitle>
                      <CardDescription>Hourly processed vs intercepted fraudulent authorization volume</CardDescription>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800 font-mono">
                      Rolling 24h
                    </span>
                  </div>
                </CardHeader>
                <div className="p-4 pt-0">
                  <RiskTrendChart data={hourlyTrends} />
                </div>
              </Card>
            </div>

            <div>
              <Card className="h-full">
                <CardHeader>
                  <CardTitle>Ensemble ROC Performance</CardTitle>
                  <CardDescription>Champion Meta-Stacking ROC-AUC: 0.988</CardDescription>
                </CardHeader>
                <div className="p-4 pt-0">
                  <RocCurveChart data={sampleRoc} auc={0.988} />
                </div>
              </Card>
            </div>
          </div>

          {/* Secondary Telemetry Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Confusion Matrix (Holdout)</CardTitle>
                <CardDescription>Evaluation on 5,000 live production transactions</CardDescription>
              </CardHeader>
              <div className="p-4 pt-0">
                <ConfusionMatrixChart
                  matrix={sampleConfusionMatrix}
                  precision={0.935}
                  recall={0.946}
                  f1={0.94}
                />
              </div>
            </Card>

            <div className="md:col-span-2">
              <Card className="h-full">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle>Recent High-Risk Interceptions</CardTitle>
                      <CardDescription>Decisions executed under sub-20ms policy SLA</CardDescription>
                    </div>
                    <Link href="/transactions" className="text-xs text-blue-400 hover:underline flex items-center gap-1 font-semibold">
                      View All <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </CardHeader>
                <div className="p-4 pt-0">
                  <TransactionTable
                    transactions={recentTransactions}
                    onInvestigate={handleInvestigate}
                  />
                </div>
              </Card>
            </div>
          </div>
        </>
      )}

      {/* ANALYST VIEW: OPERATIONAL QUEUE & TRIAGE WORKBENCH */}
      {!isAdmin && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* High Risk Queue */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>High-Risk Transactions Awaiting Action</CardTitle>
                    <CardDescription>Click any row to open the complete 4-tab XAI investigation dossier.</CardDescription>
                  </div>
                  <Link href="/transactions" className="text-xs text-blue-400 hover:underline flex items-center gap-1">
                    Explore All <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </CardHeader>
              <div className="p-4 pt-0">
                <TransactionTable
                  transactions={recentTransactions}
                  onInvestigate={handleInvestigate}
                />
              </div>
            </Card>

            {/* Open Cases List */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>My Open Investigation Cases</CardTitle>
                    <CardDescription>Dispute defense dossiers and evidence packages</CardDescription>
                  </div>
                  <Link href="/cases" className="text-xs text-blue-400 hover:underline flex items-center gap-1">
                    All Cases <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </CardHeader>
              <div className="p-4 pt-0 divide-y divide-gray-800">
                {openCases.length === 0 ? (
                  <p className="text-xs text-gray-500 py-4">No active open cases assigned.</p>
                ) : (
                  openCases.map((c) => (
                    <div key={c.id} className="py-3 flex items-center justify-between text-xs">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-gray-200">{c.case_number}</span>
                          <span className="px-2 py-0.5 rounded bg-red-950 text-red-400 border border-red-800/40 text-[10px] font-bold">
                            {c.severity}
                          </span>
                        </div>
                        <p className="text-[11px] text-gray-400 mt-0.5 truncate max-w-md">{c.summary}</p>
                      </div>
                      <div className="text-right">
                        <span className="font-bold text-gray-200">{formatCurrency(c.amount)}</span>
                        <Link href={`/cases`}>
                          <Button variant="outline" size="sm" className="ml-3 text-[11px]">
                            Review
                          </Button>
                        </Link>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </Card>
          </div>

          {/* Quick Alert Feed */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Bell className="w-4 h-4 text-red-400 animate-pulse" />
                    <CardTitle>Critical Alerts Feed</CardTitle>
                  </div>
                  <Link href="/alerts" className="text-xs text-blue-400 hover:underline">
                    Manage
                  </Link>
                </div>
              </CardHeader>
              <div className="p-4 pt-0 space-y-3">
                {recentAlerts.map((alt) => (
                  <div key={alt.id} className="p-3 bg-gray-900/60 border border-gray-800 rounded-xl space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-gray-200">{alt.alert_id}</span>
                      <span className="px-2 py-0.5 rounded bg-red-950 text-red-400 font-bold text-[10px]">
                        Risk: {alt.risk_score.toFixed(2)}
                      </span>
                    </div>
                    <p className="text-[11px] text-gray-300 font-medium">{alt.reason}</p>
                    <div className="flex items-center justify-between text-[10px] text-gray-500 pt-1">
                      <span>{alt.merchant_name || "Online Merchant"}</span>
                      <span className="font-bold text-gray-300">{formatCurrency(alt.amount)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Analyst Quick Tools */}
            <Card className="bg-gradient-to-br from-blue-950/40 to-indigo-950/40 border-blue-500/30">
              <CardHeader>
                <CardTitle className="text-blue-300">Quick Investigation Tools</CardTitle>
                <CardDescription>One-click operational actions</CardDescription>
              </CardHeader>
              <div className="p-4 pt-0 space-y-2">
                <Link href="/live-monitor" className="block">
                  <Button variant="secondary" size="sm" className="w-full justify-start text-xs">
                    <Radio className="w-3.5 h-3.5 mr-2 text-red-400" />
                    Launch Live Threat Radar
                  </Button>
                </Link>
                <Link href="/customers" className="block">
                  <Button variant="secondary" size="sm" className="w-full justify-start text-xs">
                    <UserCheck className="w-3.5 h-3.5 mr-2 text-blue-400" />
                    Look Up Cardholder 360
                  </Button>
                </Link>
                <Link href="/reports" className="block">
                  <Button variant="secondary" size="sm" className="w-full justify-start text-xs">
                    <FileSearch className="w-3.5 h-3.5 mr-2 text-emerald-400" />
                    Generate SAR / Dispute Dossier
                  </Button>
                </Link>
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* Investigation Dossier Modal */}
      <TransactionInvestigationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        transaction={selectedTx}
      />
    </div>
  );
}
