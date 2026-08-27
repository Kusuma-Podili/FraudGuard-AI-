"use client";

import React, { useState } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";
import { LiveTransactionFeed } from "@/components/transactions/LiveTransactionFeed";
import { ShapWaterfallChart } from "@/components/xai/ShapWaterfallChart";
import { Modal } from "@/components/ui/Modal";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { StreamTransactionEvent, ExplainabilityData } from "@/types";
import { api } from "@/lib/api";
import { Radio, Play, Pause, Trash2, ShieldCheck, Activity, MapPin } from "lucide-react";
import { formatCurrency, getActionBadge } from "@/lib/utils";

export default function LiveMonitorPage() {
  const { events, isConnected, isPaused, togglePause, clearEvents } = useWebSocket(80);
  const [selectedEvent, setSelectedEvent] = useState<StreamTransactionEvent | null>(null);
  const [xaiData, setXaiData] = useState<ExplainabilityData | null>(null);
  const [isLoadingXai, setIsLoadingXai] = useState(false);

  const handleSelectEvent = async (evt: StreamTransactionEvent) => {
    setSelectedEvent(evt);
    setIsLoadingXai(true);
    try {
      const data = await api.getExplanation(evt.transaction_id, {
        amount: evt.amount,
        merchant_category: evt.category,
        country_code: evt.country,
        card_id: evt.card_id,
      });
      setXaiData(data);
    } catch (e) {
      console.error("Failed to load XAI explanation", e);
    } finally {
      setIsLoadingXai(false);
    }
  };

  const highRiskCount = events.filter((e) => e.risk_tier === "HIGH" || e.risk_tier === "CRITICAL").length;
  const declineCount = events.filter((e) => e.decision_action === "DECLINE").length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Radio className="w-5 h-5 text-red-500 animate-pulse" />
            <h1 className="text-2xl font-bold text-gray-100 tracking-tight">Live Threat Radar</h1>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Real-time streaming authorization feed connected via low-latency WebSockets.
          </p>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={togglePause}>
            {isPaused ? <Play className="w-3.5 h-3.5 mr-1" /> : <Pause className="w-3.5 h-3.5 mr-1" />}
            {isPaused ? "Resume Stream" : "Pause Stream"}
          </Button>
          <Button variant="outline" size="sm" onClick={clearEvents}>
            <Trash2 className="w-3.5 h-3.5 mr-1" />
            Clear
          </Button>
        </div>
      </div>

      {/* Stream Metric Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 bg-gray-900/60 border border-gray-800 rounded-xl">
          <span className="text-[11px] text-gray-400 font-medium uppercase">Socket State</span>
          <div className="flex items-center gap-2 mt-1">
            <span className={`w-2.5 h-2.5 rounded-full ${isConnected ? "bg-emerald-500 animate-ping" : "bg-red-500"}`} />
            <span className="text-sm font-bold text-gray-100">{isConnected ? "CONNECTED" : "DISCONNECTED"}</span>
          </div>
        </div>

        <div className="p-4 bg-gray-900/60 border border-gray-800 rounded-xl">
          <span className="text-[11px] text-gray-400 font-medium uppercase">Events in Buffer</span>
          <p className="text-sm font-bold text-gray-100 mt-1">{events.length} transactions</p>
        </div>

        <div className="p-4 bg-gray-900/60 border border-gray-800 rounded-xl">
          <span className="text-[11px] text-amber-400 font-medium uppercase">High Risk Intercepts</span>
          <p className="text-sm font-bold text-amber-300 mt-1">{highRiskCount}</p>
        </div>

        <div className="p-4 bg-gray-900/60 border border-gray-800 rounded-xl">
          <span className="text-[11px] text-red-400 font-medium uppercase">Total Declined</span>
          <p className="text-sm font-bold text-red-400 mt-1">{declineCount}</p>
        </div>
      </div>

      {/* Live Transaction Feed Card */}
      <Card>
        <CardHeader>
          <div>
            <CardTitle>Streaming Ingestion Feed</CardTitle>
            <CardDescription>Click any event card to view instant SHAP feature waterfall breakdown.</CardDescription>
          </div>
        </CardHeader>
        <LiveTransactionFeed events={events} onSelectEvent={handleSelectEvent} />
      </Card>

      {/* SHAP / XAI Explanation Modal */}
      {selectedEvent && (
        <Modal
          isOpen={!!selectedEvent}
          onClose={() => setSelectedEvent(null)}
          title={`Explainability Dossier: ${selectedEvent.transaction_id}`}
          maxWidth="2xl"
        >
          <div className="space-y-6">
            {/* Quick Meta */}
            <div className="grid grid-cols-3 gap-3 p-3 bg-gray-950 rounded-xl border border-gray-800 text-center">
              <div>
                <span className="text-[10px] text-gray-500 uppercase">Amount</span>
                <p className="text-sm font-bold text-gray-100 mt-0.5">{formatCurrency(selectedEvent.amount)}</p>
              </div>
              <div>
                <span className="text-[10px] text-gray-500 uppercase">Decision</span>
                <p className="text-sm font-bold text-red-400 mt-0.5">{selectedEvent.decision_action}</p>
              </div>
              <div>
                <span className="text-[10px] text-gray-500 uppercase">Latency</span>
                <p className="text-sm font-bold text-emerald-400 mt-0.5">{selectedEvent.latency_ms.toFixed(1)} ms</p>
              </div>
            </div>

            {isLoadingXai ? (
              <div className="p-12 text-center text-gray-400">
                <Activity className="w-6 h-6 animate-spin mx-auto text-blue-400 mb-2" />
                <p className="text-xs">Computing TreeSHAP local attributions...</p>
              </div>
            ) : xaiData ? (
              <ShapWaterfallChart
                baseValue={xaiData.base_value}
                finalScore={xaiData.risk_score}
                items={xaiData.waterfall}
              />
            ) : (
              <p className="text-xs text-gray-400">No explanation available for this transaction.</p>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
}
