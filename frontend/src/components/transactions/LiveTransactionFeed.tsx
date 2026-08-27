"use client";

import React from "react";
import { StreamTransactionEvent } from "@/types";
import { formatCurrency, getActionBadge, getRiskColor, formatTimeAgo } from "@/lib/utils";
import { Zap, AlertTriangle, ShieldCheck, Navigation } from "lucide-react";

interface LiveTransactionFeedProps {
  events: StreamTransactionEvent[];
  onSelectEvent?: (event: StreamTransactionEvent) => void;
}

export const LiveTransactionFeed: React.FC<LiveTransactionFeedProps> = ({
  events,
  onSelectEvent,
}) => {
  return (
    <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
      {events.length === 0 ? (
        <div className="p-8 text-center border border-dashed border-gray-800 rounded-xl">
          <Zap className="w-8 h-8 text-gray-600 mx-auto animate-pulse" />
          <p className="text-xs text-gray-400 mt-2">Waiting for live transaction stream...</p>
        </div>
      ) : (
        events.map((evt, idx) => {
          const badge = getActionBadge(evt.decision_action);
          const isHighRisk = evt.risk_tier === "HIGH" || evt.risk_tier === "CRITICAL";

          return (
            <div
              key={evt.transaction_id + idx}
              onClick={() => onSelectEvent?.(evt)}
              className={`p-3.5 bg-gray-900/80 border rounded-xl flex items-center justify-between gap-4 cursor-pointer transition-all hover:bg-gray-850 hover:scale-[1.01] ${
                isHighRisk ? "border-red-500/40 bg-red-950/20" : "border-gray-800"
              }`}
            >
              {/* Icon & Details */}
              <div className="flex items-center gap-3">
                <div
                  className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${
                    isHighRisk ? "bg-red-500/20 text-red-400" : "bg-blue-500/20 text-blue-400"
                  }`}
                >
                  {isHighRisk ? <AlertTriangle className="w-4 h-4" /> : <Zap className="w-4 h-4" />}
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-gray-100">{evt.merchant_name}</span>
                    <span className="text-[10px] text-gray-500 font-mono">({evt.card_id})</span>
                    {evt.is_impossible_travel && (
                      <span className="inline-flex items-center gap-0.5 px-1.5 py-0.2 rounded text-[9px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40">
                        <Navigation className="w-2.5 h-2.5" /> Impossible Travel
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 mt-0.5 text-[11px] text-gray-400">
                    <span>{evt.category}</span>
                    <span>•</span>
                    <span>{evt.country}</span>
                    <span>•</span>
                    <span className="font-mono text-gray-500">{evt.latency_ms.toFixed(1)}ms</span>
                  </div>
                </div>
              </div>

              {/* Amount & Decision */}
              <div className="text-right shrink-0">
                <p className="text-xs font-bold text-gray-100">{formatCurrency(evt.amount)}</p>
                <div className="flex items-center gap-1.5 mt-1 justify-end">
                  <span className="font-mono text-[11px] font-bold text-gray-300">{(evt.risk_score * 100).toFixed(1)}%</span>
                  <span className={`px-1.5 py-0.5 rounded text-[9px] font-semibold ${badge.className}`}>
                    {badge.label}
                  </span>
                </div>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
};
