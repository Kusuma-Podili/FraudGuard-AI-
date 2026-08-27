"use client";

import React from "react";
import { useAnalytics } from "@/hooks/useAnalytics";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { RiskTrendChart } from "@/components/charts/RiskTrendChart";
import { MetricCard } from "@/components/ui/MetricCard";
import { formatCurrency } from "@/lib/utils";
import { BarChart3, Globe, Store, ShieldCheck, DollarSign, Activity } from "lucide-react";

export default function AnalyticsPage() {
  const { kpis, hourlyTrends, merchants, geoData, isLoading } = useAnalytics();

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-100 tracking-tight">Fraud Analytics & Risk Intelligence</h1>
        <p className="text-xs text-gray-400 mt-1">
          Deep geographic risk indices, merchant acquisition monitoring, and economic loss prevention.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total 24h Intercepted"
          value={kpis ? formatCurrency(kpis.fraud_prevented_usd_24h) : "$184,200.00"}
          subtitle="99.4% Precision"
          icon={<DollarSign className="w-5 h-5 text-emerald-400" />}
        />
        <MetricCard
          title="Total Gross Volume"
          value={kpis ? formatCurrency(kpis.total_volume_usd_24h) : "$4,820,000.00"}
          subtitle="Processed Across All Merchants"
          icon={<Activity className="w-5 h-5 text-blue-400" />}
        />
        <MetricCard
          title="System TPS Throughput"
          value={kpis ? `${kpis.system_tps} TPS` : "120 TPS"}
          subtitle="Sub-20ms SLA"
          icon={<ShieldCheck className="w-5 h-5 text-purple-400" />}
        />
        <MetricCard
          title="Active Threat Index"
          value={kpis?.active_threat_level || "NORMAL"}
          subtitle="Anomaly Detector Status"
          icon={<BarChart3 className="w-5 h-5 text-amber-400" />}
        />
      </div>

      {/* Hourly Trend Chart */}
      <Card>
        <CardHeader>
          <div>
            <CardTitle>24-Hour Authorizations vs Fraud Interceptions</CardTitle>
            <CardDescription>Continuous trend of gross processed volume vs intercepted dollar amounts.</CardDescription>
          </div>
        </CardHeader>
        <RiskTrendChart data={hourlyTrends} />
      </Card>

      {/* Merchants & Geo Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Merchant Risk Table */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Store className="w-4 h-4 text-blue-400" />
              <CardTitle>High-Risk Merchant Profiles</CardTitle>
            </div>
          </CardHeader>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-gray-300">
              <thead className="bg-gray-950/80 text-[10px] text-gray-400 uppercase border-b border-gray-800">
                <tr>
                  <th className="py-2.5 px-3">Merchant</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Fraud Rate</th>
                  <th className="py-2.5 px-3">Risk Score</th>
                  <th className="py-2.5 px-3 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {merchants.map((m) => (
                  <tr key={m.merchant_id} className="hover:bg-gray-800/40">
                    <td className="py-2.5 px-3 font-semibold text-gray-200">{m.name}</td>
                    <td className="py-2.5 px-3 text-gray-400">{m.category}</td>
                    <td className="py-2.5 px-3 font-mono text-red-400">{(m.fraud_rate * 100).toFixed(1)}%</td>
                    <td className="py-2.5 px-3 font-mono font-bold text-amber-400">{(m.risk_score * 100).toFixed(0)}</td>
                    <td className="py-2.5 px-3 text-right">
                      <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${
                        m.is_blacklisted ? "bg-red-950 text-red-400 border border-red-500/30" : "bg-emerald-950 text-emerald-400 border border-emerald-500/30"
                      }`}>
                        {m.is_blacklisted ? "BLACKLISTED" : "MONITORED"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Geo Risk Table */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-purple-400" />
              <CardTitle>Geographic Risk Index</CardTitle>
            </div>
          </CardHeader>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-gray-300">
              <thead className="bg-gray-950/80 text-[10px] text-gray-400 uppercase border-b border-gray-800">
                <tr>
                  <th className="py-2.5 px-3">Country</th>
                  <th className="py-2.5 px-3">ISO</th>
                  <th className="py-2.5 px-3">Volume</th>
                  <th className="py-2.5 px-3">Fraud Count</th>
                  <th className="py-2.5 px-3 text-right">Risk Index</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {geoData.map((g) => (
                  <tr key={g.country_code} className="hover:bg-gray-800/40">
                    <td className="py-2.5 px-3 font-semibold text-gray-200">{g.country_name}</td>
                    <td className="py-2.5 px-3 font-mono text-gray-400">{g.country_code}</td>
                    <td className="py-2.5 px-3 font-mono">{g.transaction_count}</td>
                    <td className="py-2.5 px-3 font-mono text-red-400">{g.fraud_count}</td>
                    <td className="py-2.5 px-3 text-right font-mono font-bold text-amber-400">
                      {(g.risk_score * 100).toFixed(0)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}
