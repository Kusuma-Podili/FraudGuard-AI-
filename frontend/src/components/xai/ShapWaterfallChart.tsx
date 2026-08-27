"use client";

import React from "react";
import { ShapWaterfallItem } from "@/types";
import { ArrowUpRight, ArrowDownRight, Info } from "lucide-react";
import { cn } from "@/lib/utils";

interface ShapWaterfallChartProps {
  baseValue: number;
  finalScore: number;
  items: ShapWaterfallItem[];
}

export const ShapWaterfallChart: React.FC<ShapWaterfallChartProps> = ({
  baseValue,
  finalScore,
  items,
}) => {
  return (
    <div className="w-full space-y-4">
      {/* Summary Banner */}
      <div className="flex items-center justify-between p-3.5 bg-gray-950/80 border border-gray-800 rounded-xl">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400">
            <Info className="w-4 h-4" />
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-200">SHAP Local Feature Attribution</p>
            <p className="text-[11px] text-gray-400">Baseline Prior Rate: {(baseValue * 100).toFixed(1)}%</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-[11px] text-gray-400">Final Predicted Probability</p>
          <p className="text-base font-bold text-gray-100 font-mono">{(finalScore * 100).toFixed(1)}%</p>
        </div>
      </div>

      {/* Waterfall Bars */}
      <div className="space-y-2.5">
        {items.map((item, idx) => {
          const isRisk = item.direction === "INCREASES_RISK";
          const barWidth = Math.min(100, Math.max(8, item.impact_pct * 1.5));

          return (
            <div
              key={idx}
              className="p-3 bg-gray-900/60 border border-gray-800 rounded-xl flex items-center justify-between gap-4 hover:border-gray-700 transition-colors"
            >
              {/* Feature label and value */}
              <div className="w-1/3">
                <div className="flex items-center gap-2">
                  {isRisk ? (
                    <ArrowUpRight className="w-4 h-4 text-red-400 shrink-0" />
                  ) : (
                    <ArrowDownRight className="w-4 h-4 text-emerald-400 shrink-0" />
                  )}
                  <span className="text-xs font-semibold text-gray-200 truncate">{item.feature}</span>
                </div>
                <p className="text-[10px] text-gray-400 mt-0.5 font-mono ml-6">Value: {String(item.value)}</p>
              </div>

              {/* Graphical Visual Bar */}
              <div className="flex-1">
                <div className="w-full bg-gray-950 rounded-full h-3 overflow-hidden border border-gray-800">
                  <div
                    className={cn("h-full rounded-full transition-all duration-500", isRisk ? "bg-gradient-to-r from-red-600 to-red-400" : "bg-gradient-to-r from-emerald-600 to-emerald-400")}
                    style={{ width: `${barWidth}%` }}
                  />
                </div>
              </div>

              {/* Numerical Shapley Value */}
              <div className="w-24 text-right">
                <span
                  className={cn(
                    "text-xs font-bold font-mono px-2 py-0.5 rounded",
                    isRisk ? "bg-red-950/60 text-red-400" : "bg-emerald-950/60 text-emerald-400"
                  )}
                >
                  {isRisk ? "+" : ""}{(item.shap_value * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
