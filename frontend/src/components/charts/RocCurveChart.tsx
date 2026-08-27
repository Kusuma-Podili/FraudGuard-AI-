"use client";

import React from "react";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

interface RocPoint {
  fpr: number;
  tpr: number;
}

interface RocCurveChartProps {
  data: RocPoint[];
  aucScore?: number;
}

export const RocCurveChart: React.FC<RocCurveChartProps> = ({ data, aucScore = 0.988 }) => {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-400">Receiver Operating Characteristic (ROC)</span>
        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-950/60 text-blue-400 border border-blue-500/30 font-mono">
          AUC = {aucScore.toFixed(3)}
        </span>
      </div>
      <div className="w-full h-56">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 10, left: -25, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
            <XAxis dataKey="fpr" stroke="#6B7280" tick={{ fontSize: 10 }} domain={[0, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
            <YAxis stroke="#6B7280" tick={{ fontSize: 10 }} domain={[0, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
            <Tooltip
              contentStyle={{ backgroundColor: "#111827", borderColor: "#374151", borderRadius: "0.5rem", fontSize: "11px" }}
              formatter={(val: any, name: string) => [`${(val * 100).toFixed(1)}%`, name === "tpr" ? "True Positive Rate" : "False Positive Rate"]}
            />
            <Line type="monotone" dataKey="tpr" stroke="#3B82F6" strokeWidth={3} dot={{ r: 3, fill: "#60A5FA" }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
