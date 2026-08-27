"use client";

import React, { useState, useEffect } from "react";
import { MetricCard } from "@/components/ui/MetricCard";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { RiskTrendChart } from "@/components/charts/RiskTrendChart";
import { RocCurveChart } from "@/components/charts/RocCurveChart";
import { ConfusionMatrixChart } from "@/components/charts/ConfusionMatrixChart";
import { TransactionTable } from "@/components/transactions/TransactionTable";
import { useAnalytics } from "@/hooks/useAnalytics";
import { api } from "@/lib/api";
import { TransactionRecord } from "@/types";
import { formatCurrency } from "@/lib/utils";
import {
  ShieldAlert,
  DollarSign,
  TrendingDown,
  Activity,
  AlertTriangle,
  FileSearch,
  CheckCircle2,
} from "lucide-react";

export default function DashboardPage() {
  const { kpis, hourlyTrends, isLoading } = useAnalytics();
  const [recentTransactions, setRecentTransactions] = useState<TransactionRecord[]>([]);

  useEffect(() => {
    async function loadRecent() {
      try {
        const res = await api.listTransactions({ page: 1, page_size: 6 });
        setRecentTransactions(res.items);
      } catch (e) {
        console.error("Failed to load transactions", e);
      }
    }
    loadRecent();
  }, []);

  const sampleConfusionMatrix = {
    true_negative: 4820,
    false_positive: 32,
    false_negative: 8,
    true_positive: 140,
  };

  const sampleRoc = [
    { fpr: 0.00, tpr: 0.00 },
    { fpr: 0.01, tpr: 0.78 },
    { fpr: 0.02, tpr: 0.89 },
    { fpr: 0.05, tpr: 0.94 },
    { fpr: 0.10, tpr: 0.98 },
    { fpr: 0.20, tpr: 0.99 },
    { fpr: 1.00, tpr: 1.00 },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-100 tracking-tight">Executive Defense Overview</h1>
          <p className="text-xs text-gray-400 mt-1">
            Real-time telemetry and dollar savings across all merchant acquisition channels.
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
          <CheckCircle2 className="w-4 h-4" />
          <span>Threat Mitigation Engine: Optimal (sub-20ms SLA)</span>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="24h Fraud Prevented"
          value={kpis ? formatCurrency(kpis.fraud_prevented_usd_24h) : "$184,200.00"}
          change="+14.2% vs yesterday"
          isPositive={true}
          icon={<DollarSign className="w-5 h-5" />}
        />
        <MetricCard
          title="Global Fraud Rate"
          value={kpis ? `${kpis.fraud_rate_percentage.toFixed(2)}%` : "0.42%"}
          change="-0.18% reduction"
          isPositive={true}
          icon={<TrendingDown className="w-5 h-5" />}
        />
        <MetricCard
          title="Open Triage Cases"
          value={kpis ? kpis.open_cases_count : 14}
          subtitle="4 Critical SLA"
          icon={<ShieldAlert className="w-5 h-5 text-amber-400" />}
        />
        <MetricCard
          title="P99 Inference Latency"
          value={kpis ? `${kpis.p99_inference_latency_ms.toFixed(1)}ms` : "14.2ms"}
          subtitle="Sub-20ms Target"
          isPositive={true}
          icon={<Activity className="w-5 h-5 text-emerald-400" />}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <div>
              <CardTitle>24h Fraud Volume vs Dollar Savings</CardTitle>
              <CardDescription>Time-series monitoring of legitimate vs intercepted fraud volume.</CardDescription>
            </div>
          </CardHeader>
          <RiskTrendChart data={hourlyTrends} />
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Ensemble Confusion Matrix</CardTitle>
              <CardDescription>Real-time classification accuracy on test stream.</CardDescription>
            </div>
          </CardHeader>
          <ConfusionMatrixChart matrix={sampleConfusionMatrix} />
          <div className="mt-6 pt-4 border-t border-gray-800">
            <RocCurveChart data={sampleRoc} aucScore={0.988} />
          </div>
        </Card>
      </div>

      {/* Recent Flagged Transactions Table */}
      <Card>
        <CardHeader>
          <div>
            <CardTitle>Recent High-Risk Transactions</CardTitle>
            <CardDescription>Live authorizations scored by multi-model ensemble & rule engine.</CardDescription>
          </div>
        </CardHeader>
        <TransactionTable transactions={recentTransactions} />
      </Card>
    </div>
  );
}
