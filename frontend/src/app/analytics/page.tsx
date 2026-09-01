"use client";

import React, { useState, useEffect } from "react";
import { useAnalytics } from "@/hooks/useAnalytics";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { RiskTrendChart } from "@/components/charts/RiskTrendChart";
import { MetricCard } from "@/components/ui/MetricCard";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";
import {
  BarChart3,
  Globe,
  Store,
  ShieldCheck,
  DollarSign,
  Activity,
  Layers,
  CreditCard,
  UserCheck,
  TrendingDown,
  Clock,
  Calendar,
} from "lucide-react";

export default function AnalyticsPage() {
  const { hourlyTrends, merchants, geoData, isLoading } = useAnalytics();
  const [dateRange, setDateRange] = useState("30d");
  const [kpis, setKpis] = useState<any>(null);

  useEffect(() => {
    async function loadKPIs() {
      try {
        const data = await api.getDashboardKPIs(dateRange);
        setKpis(data);
      } catch (e) {
        console.error("Failed to load analytics KPIs", e);
      }
    }
    loadKPIs();
  }, [dateRange]);

  const categoriesData = [
    { name: "Electronics & High-Tech", code: "ELECTRONICS", txCount: 3420, fraudRate: "4.15%", riskScore: 0.58, volume: "$1,250,000" },
    { name: "Crypto Asset Exchanges", code: "CRYPTO_EXCHANGE", txCount: 890, fraudRate: "11.01%", riskScore: 0.72, volume: "$740,000" },
    { name: "Luxury Goods & Jewelry", code: "LUXURY_JEWELRY", txCount: 420, fraudRate: "9.05%", riskScore: 0.64, volume: "$950,000" },
    { name: "Airlines & Travel", code: "TRAVEL_AIRLINE", txCount: 2150, fraudRate: "2.88%", riskScore: 0.35, volume: "$890,000" },
    { name: "General E-Commerce", code: "E_COMMERCE", txCount: 12400, fraudRate: "1.69%", riskScore: 0.28, volume: "$2,400,000" },
    { name: "Grocery & Supermarkets", code: "GROCERY", txCount: 28500, fraudRate: "0.30%", riskScore: 0.08, volume: "$1,850,000" },
  ];

  const channelsData = [
    { channel: "Online / CNP Web Checkout", share: "45.2%", fraudRate: "1.50%", status: "High Surveillance" },
    { channel: "Mobile In-App Purchases", share: "32.1%", fraudRate: "0.81%", status: "Biometric Verified" },
    { channel: "POS Contactless (NFC / ApplePay)", share: "14.5%", fraudRate: "0.30%", status: "Tokenized" },
    { channel: "POS EMV Physical Chip", share: "6.2%", fraudRate: "0.15%", status: "Chip & PIN" },
    { channel: "ATM Cash Advance", share: "2.0%", fraudRate: "1.76%", status: "Velocity Monitored" },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Header & Range Filters */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-blue-400" />
            <h1 className="text-2xl font-bold text-gray-100 tracking-tight">Fraud Analytics & Risk Intelligence</h1>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Deep multi-dimensional analysis of authorizations, MCC exposure, payment channels, and team productivity.
          </p>
        </div>

        {/* Date Filters */}
        <div className="flex items-center gap-1.5 p-1 bg-gray-950 border border-gray-800 rounded-xl">
          {[
            { id: "today", label: "Today (24h)" },
            { id: "7d", label: "Last 7 Days" },
            { id: "30d", label: "Last 30 Days" },
            { id: "90d", label: "Last 90 Days" },
          ].map((d) => (
            <button
              key={d.id}
              onClick={() => setDateRange(d.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                dateRange === d.id
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-500/20"
                  : "text-gray-400 hover:text-gray-200"
              }`}
            >
              {d.label}
            </button>
          ))}
        </div>
      </div>

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Fraud Prevented"
          value={kpis ? formatCurrency(kpis.fraud_prevented_usd || 184200.0) : "$184,200.00"}
          change="+14.2% dollar savings"
          isPositive={true}
          icon={<DollarSign className="w-5 h-5 text-emerald-400" />}
        />
        <MetricCard
          title="Global Fraud Rate"
          value={kpis ? `${(kpis.fraud_rate_pct || 0.42).toFixed(2)}%` : "0.42%"}
          change="-0.18% reduction"
          isPositive={true}
          icon={<TrendingDown className="w-5 h-5 text-blue-400" />}
        />
        <MetricCard
          title="Total Gross Volume"
          value={kpis ? formatCurrency(kpis.total_volume_usd || 8450200.0) : "$8,450,200.00"}
          subtitle="Processed Across All Merchants"
          icon={<Activity className="w-5 h-5 text-purple-400" />}
        />
        <MetricCard
          title="P99 Inference Latency"
          value={kpis ? `${(kpis.p99_inference_latency_ms || 14.2).toFixed(1)}ms` : "14.2ms"}
          subtitle="Sub-20ms SLA Guarantee"
          isPositive={true}
          icon={<ShieldCheck className="w-5 h-5 text-amber-400" />}
        />
      </div>

      {/* Hourly Trend Chart */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Fraud Velocity & Dollar Exposure Trend</CardTitle>
              <CardDescription>Continuous time-series tracking of total volume vs blocked fraudulent transactions.</CardDescription>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800 font-mono">
              Live Aggregate
            </span>
          </div>
        </CardHeader>
        <div className="p-4 pt-0">
          <RiskTrendChart data={hourlyTrends} />
        </div>
      </Card>

      {/* Category Breakdown & Channel Risk Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Risk */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-400" />
              <CardTitle>Merchant MCC Category Risk Profile</CardTitle>
            </div>
          </CardHeader>
          <div className="p-4 pt-0 overflow-x-auto">
            <table className="w-full text-left text-xs text-gray-300">
              <thead className="bg-gray-950/80 text-[10px] text-gray-400 uppercase border-b border-gray-800">
                <tr>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Volume</th>
                  <th className="py-2.5 px-3">Fraud Rate</th>
                  <th className="py-2.5 px-3 text-right">Risk Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {categoriesData.map((cat, i) => (
                  <tr key={i} className="hover:bg-gray-900/40">
                    <td className="py-2.5 px-3 font-semibold text-gray-200">{cat.name}</td>
                    <td className="py-2.5 px-3 text-gray-400">{cat.volume}</td>
                    <td className="py-2.5 px-3 font-mono font-bold text-red-400">{cat.fraudRate}</td>
                    <td className="py-2.5 px-3 text-right">
                      <span className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] ${cat.riskScore > 0.6 ? "bg-red-950 text-red-400 border border-red-800/40" : "bg-emerald-950 text-emerald-400 border border-emerald-800/40"}`}>
                        {(cat.riskScore * 100).toFixed(0)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Channel Breakdown */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-purple-400" />
              <CardTitle>Transaction Channel Distribution</CardTitle>
            </div>
          </CardHeader>
          <div className="p-4 pt-0 space-y-3">
            {channelsData.map((ch, idx) => (
              <div key={idx} className="p-3 bg-gray-950/60 border border-gray-800 rounded-xl space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-gray-200">{ch.channel}</span>
                  <span className="font-mono font-bold text-blue-400">{ch.share}</span>
                </div>
                <div className="flex items-center justify-between text-[11px] text-gray-500">
                  <span>Fraud Rate: <strong className="text-red-400">{ch.fraudRate}</strong></span>
                  <span className="text-emerald-400 font-medium">{ch.status}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* High-Risk Merchants & Geographic Heatmap Data */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Merchant Profiles */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Store className="w-4 h-4 text-blue-400" />
              <CardTitle>Monitored High-Risk Merchants</CardTitle>
            </div>
          </CardHeader>
          <div className="p-4 pt-0 overflow-x-auto">
            <table className="w-full text-left text-xs text-gray-300">
              <thead className="bg-gray-950/80 text-[10px] text-gray-400 uppercase border-b border-gray-800">
                <tr>
                  <th className="py-2.5 px-3">Merchant</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Fraud Rate</th>
                  <th className="py-2.5 px-3 text-right">Risk Index</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {merchants.map((m) => (
                  <tr key={m.merchant_id} className="hover:bg-gray-900/40">
                    <td className="py-2.5 px-3 font-semibold text-gray-200">{m.name}</td>
                    <td className="py-2.5 px-3 text-gray-400">{m.category}</td>
                    <td className="py-2.5 px-3 font-mono text-red-400">{(m.fraud_rate * 100).toFixed(1)}%</td>
                    <td className="py-2.5 px-3 text-right font-mono font-bold text-amber-400">
                      {(m.risk_score * 100).toFixed(0)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Country Geo Heatmap */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-emerald-400" />
              <CardTitle>Geographic Fraud Risk Corridors</CardTitle>
            </div>
          </CardHeader>
          <div className="p-4 pt-0 space-y-2.5">
            {geoData.map((g) => (
              <div key={g.country_code} className="flex items-center justify-between p-3 bg-gray-950/60 border border-gray-800 rounded-xl text-xs">
                <div>
                  <span className="font-bold text-gray-200">{g.country_name} ({g.country_code})</span>
                  <p className="text-[10px] text-gray-500">{g.total_transactions.toLocaleString()} Authorizations</p>
                </div>
                <div className="text-right">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${g.risk_index > 0.4 ? "bg-red-950 text-red-400" : "bg-emerald-950 text-emerald-400"}`}>
                    Risk: {(g.risk_index * 100).toFixed(0)}
                  </span>
                  <p className="text-[10px] text-red-400 font-mono mt-0.5">{g.fraud_count} Flagged</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Analyst Team Case Resolution Stats */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <UserCheck className="w-4 h-4 text-blue-400" />
            <CardTitle>Analyst Operations & Resolution Productivity</CardTitle>
          </div>
        </CardHeader>
        <div className="p-4 pt-0 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { name: "Sarah Chen", resolved: 54, avgTime: "14.2 mins", accuracy: "98.2%" },
            { name: "Marcus Vance", resolved: 48, avgTime: "16.8 mins", accuracy: "96.5%" },
            { name: "Alex Rivera", resolved: 42, avgTime: "21.0 mins", accuracy: "94.8%" },
            { name: "Elena Rostova", resolved: 40, avgTime: "19.5 mins", accuracy: "97.1%" },
          ].map((an, i) => (
            <div key={i} className="p-4 bg-gray-950/60 border border-gray-800 rounded-xl space-y-2">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold text-xs">
                  {an.name.charAt(0)}
                </div>
                <div>
                  <h4 className="font-bold text-gray-200 text-xs">{an.name}</h4>
                  <p className="text-[10px] text-gray-500">Fraud Specialist</p>
                </div>
              </div>
              <div className="pt-2 border-t border-gray-800/80 grid grid-cols-3 gap-1 text-center text-xs">
                <div>
                  <span className="text-[9px] text-gray-500 block">Resolved</span>
                  <span className="font-bold text-gray-200">{an.resolved}</span>
                </div>
                <div>
                  <span className="text-[9px] text-gray-500 block">Avg Time</span>
                  <span className="font-bold text-blue-400">{an.avgTime}</span>
                </div>
                <div>
                  <span className="text-[9px] text-gray-500 block">Accuracy</span>
                  <span className="font-bold text-emerald-400">{an.accuracy}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
