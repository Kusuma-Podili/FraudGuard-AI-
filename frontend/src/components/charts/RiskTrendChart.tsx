"use client";

import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { HourlyTrendPoint } from "@/types";
import { formatCurrency } from "@/lib/utils";

interface RiskTrendChartProps {
  data: HourlyTrendPoint[];
}

export const RiskTrendChart: React.FC<RiskTrendChartProps> = ({ data }) => {
  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="fraudGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#EF4444" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#EF4444" stopOpacity={0.0} />
            </linearGradient>
            <linearGradient id="volumeGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.2} />
              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
          <XAxis dataKey="hour" stroke="#6B7280" tick={{ fontSize: 11 }} />
          <YAxis stroke="#6B7280" tick={{ fontSize: 11 }} />
          <Tooltip
            contentStyle={{ backgroundColor: "#111827", borderColor: "#374151", borderRadius: "0.75rem", fontSize: "12px" }}
            formatter={(val: any, name: string) => {
              if (name === "blocked_volume_usd") return [formatCurrency(val), "Fraud Blocked (₹)"];
              if (name === "volume_usd") return [formatCurrency(val), "Total Volume (₹)"];
              return [val, name];
            }}
          />
          <Area type="monotone" dataKey="volume_usd" stroke="#3B82F6" strokeWidth={2} fillOpacity={1} fill="url(#volumeGradient)" />
          <Area type="monotone" dataKey="blocked_volume_usd" stroke="#EF4444" strokeWidth={2} fillOpacity={1} fill="url(#fraudGradient)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
