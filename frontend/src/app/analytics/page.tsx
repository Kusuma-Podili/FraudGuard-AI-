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
  DollarSign,
  Activity,
  Layers,
  CreditCard,
  UserCheck,
  TrendingDown,
  Zap,
} from "lucide-react";

export default function AnalyticsPage() {
  const { hourlyTrends, merchants, geoData } = useAnalytics();
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
    { name: "Electronics & High-Tech", code: "ELECTRONICS", txCount: 3420, fraudRate: "4.15%", riskScore: 0.58, volume: "₹12,50,000" },
    { name: "Crypto Asset Exchanges", code: "CRYPTO_EXCHANGE", txCount: 890, fraudRate: "11.01%", riskScore: 0.72, volume: "₹7,40,000" },
    { name: "Luxury Goods & Jewelry", code: "LUXURY_JEWELRY", txCount: 420, fraudRate: "9.05%", riskScore: 0.64, volume: "₹9,50,000" },
    { name: "Airlines & Travel", code: "TRAVEL_AIRLINE", txCount: 2150, fraudRate: "2.88%", riskScore: 0.35, volume: "₹8,90,000" },
    { name: "General E-Commerce", code: "E_COMMERCE", txCount: 12400, fraudRate: "1.69%", riskScore: 0.28, volume: "₹24,00,000" },
    { name: "Grocery & Supermarkets", code: "GROCERY", txCount: 28500, fraudRate: "0.30%", riskScore: 0.08, volume: "₹18,50,000" },
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
            <BarChart3 className="w-6 h-6 text-gray-800" />
            <h1 className="text-2xl font-bold text-[#111827] tracking-tight">Fraud Analytics & Risk Intelligence</h1>
          </div>
          <p className="text-xs text-[#4B5563] mt-1">
            Multi-dimensional analysis of authorizations, MCC exposure, payment channels, and team productivity.
          </p>
        </div>

        {/* Date Filters */}
        <div className="flex items-center gap-1.5 p-1 bg-white border border-[#E5E7EB] rounded-xl shadow-sm">
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
                  ? "bg-[#FB923C] text-white shadow-sm"
                  : "text-[#4B5563] hover:text-[#111827]"
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
          value={kpis ? formatCurrency(kpis.fraud_prevented_usd || 184200.0) : "₹1,84,200.00"}
          change="+14.2% rupee savings"
          isPositive={true}
          icon={<span className="font-bold text-base">₹</span>}
        />
        <MetricCard
          title="Global Fraud Rate"
          value={kpis ? `${(kpis.fraud_rate_pct || 0.42).toFixed(2)}%` : "0.42%"}
          change="-0.18% reduction"
          isPositive={true}
          icon={<TrendingDown className="w-5 h-5 text-gray-700" />}
        />
        <MetricCard
          title="Total Gross Volume"
          value={kpis ? formatCurrency(kpis.total_volume_usd || 8450200.0) : "₹84,50,200.00"}
          subtitle="Processed Across All Rails"
          icon={<Activity className="w-5 h-5 text-gray-700" />}
        />
        <MetricCard
          title="P99 Inference Latency"
          value={kpis ? `${(kpis.p99_inference_latency_ms || 14.2).toFixed(1)}ms` : "14.2ms"}
          subtitle="Sub-20ms SLA Guarantee"
          isPositive={true}
          icon={<Zap className="w-5 h-5 text-gray-700" />}
        />
      </div>

      {/* Hourly Trend Chart */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Fraud Velocity & Exposure Trend</CardTitle>
              <CardDescription>Continuous time-series tracking of total volume vs blocked fraudulent transactions in ₹.</CardDescription>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-gray-100 text-gray-700 border border-gray-300 font-mono font-semibold">
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
              <Layers className="w-4 h-4 text-gray-700" />
              <CardTitle>Merchant MCC Category Risk Profile</CardTitle>
            </div>
          </CardHeader>
          <div className="p-4 pt-0 overflow-x-auto">
            <table className="w-full text-left text-xs text-[#111827]">
              <thead className="bg-[#F9FAFB] text-[10px] text-[#4B5563] uppercase border-b border-[#E5E7EB]">
                <tr>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Volume</th>
                  <th className="py-2.5 px-3">Fraud Rate</th>
                  <th className="py-2.5 px-3 text-right">Risk Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E5E7EB]">
                {categoriesData.map((cat, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="py-2.5 px-3 font-semibold text-[#111827]">{cat.name}</td>
                    <td className="py-2.5 px-3 text-[#4B5563]">{cat.volume}</td>
                    <td className="py-2.5 px-3 font-mono font-bold text-[#EA580C]">{cat.fraudRate}</td>
                    <td className="py-2.5 px-3 text-right">
                      <span className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] ${cat.riskScore > 0.6 ? "bg-[#FFEDD5] text-[#9A3412] border border-[#FDBA74]" : "bg-gray-100 text-gray-700 border border-gray-300"}`}>
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
              <CreditCard className="w-4 h-4 text-gray-700" />
              <CardTitle>Transaction Channel Distribution</CardTitle>
            </div>
          </CardHeader>
          <div className="p-4 pt-0 space-y-3">
            {channelsData.map((ch, idx) => (
              <div key={idx} className="p-3 bg-[#F9FAFB] border border-[#E5E7EB] rounded-xl space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-[#111827]">{ch.channel}</span>
                  <span className="font-mono font-bold text-gray-900">{ch.share}</span>
                </div>
                <div className="flex items-center justify-between text-[11px] text-[#4B5563]">
                  <span>Fraud Rate: <strong className="text-[#EA580C]">{ch.fraudRate}</strong></span>
                  <span className="text-gray-700 font-medium">{ch.status}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* High-Risk Merchants & Geographic Corridors */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Merchant Profiles */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Store className="w-4 h-4 text-gray-700" />
              <CardTitle>Monitored High-Risk Merchants</CardTitle>
            </div>
          </CardHeader>
          <div className="p-4 pt-0 overflow-x-auto">
            <table className="w-full text-left text-xs text-[#111827]">
              <thead className="bg-[#F9FAFB] text-[10px] text-[#4B5563] uppercase border-b border-[#E5E7EB]">
                <tr>
                  <th className="py-2.5 px-3">Merchant</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Fraud Rate</th>
                  <th className="py-2.5 px-3 text-right">Risk Index</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E5E7EB]">
                {merchants.map((m) => (
                  <tr key={m.merchant_id} className="hover:bg-gray-50">
                    <td className="py-2.5 px-3 font-semibold text-[#111827]">{m.name}</td>
                    <td className="py-2.5 px-3 text-[#4B5563]">{m.category}</td>
                    <td className="py-2.5 px-3 font-mono text-[#EA580C] font-bold">{(m.fraud_rate * 100).toFixed(1)}%</td>
                    <td className="py-2.5 px-3 text-right font-mono font-bold text-gray-700">
                      {(m.risk_score * 100).toFixed(0)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Country Geo Corridors */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-gray-700" />
              <CardTitle>Geographic Fraud Risk Corridors</CardTitle>
            </div>
          </CardHeader>
          <div className="p-4 pt-0 space-y-2.5">
            {geoData.map((g) => (
              <div key={g.country_code} className="flex items-center justify-between p-3 bg-[#F9FAFB] border border-[#E5E7EB] rounded-xl text-xs">
                <div>
                  <span className="font-bold text-[#111827]">{g.country_name} ({g.country_code})</span>
                  <p className="text-[10px] text-[#4B5563]">{g.total_transactions.toLocaleString()} Authorizations</p>
                </div>
                <div className="text-right">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${g.risk_index > 0.4 ? "bg-[#FFEDD5] text-[#9A3412] border border-[#FDBA74]" : "bg-gray-100 text-gray-700 border border-gray-300"}`}>
                    Risk: {(g.risk_index * 100).toFixed(0)}
                  </span>
                  <p className="text-[10px] text-[#EA580C] font-mono mt-0.5">{g.fraud_count} Flagged</p>
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
            <UserCheck className="w-4 h-4 text-gray-700" />
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
            <div key={i} className="p-4 bg-[#F9FAFB] border border-[#E5E7EB] rounded-xl space-y-2">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-gray-100 text-gray-800 flex items-center justify-center font-bold text-xs">
                  {an.name.charAt(0)}
                </div>
                <div>
                  <h4 className="font-bold text-[#111827] text-xs">{an.name}</h4>
                  <p className="text-[10px] text-[#4B5563]">Fraud Specialist</p>
                </div>
              </div>
              <div className="pt-2 border-t border-[#E5E7EB] grid grid-cols-3 gap-1 text-center text-xs">
                <div>
                  <span className="text-[9px] text-[#9CA3AF] block">Resolved</span>
                  <span className="font-bold text-[#111827]">{an.resolved}</span>
                </div>
                <div>
                  <span className="text-[9px] text-[#9CA3AF] block">Avg Time</span>
                  <span className="font-bold text-gray-900">{an.avgTime}</span>
                </div>
                <div>
                  <span className="text-[9px] text-[#9CA3AF] block">Accuracy</span>
                  <span className="font-bold text-gray-900">{an.accuracy}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
