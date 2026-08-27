"use client";

import React, { useState } from "react";
import { Button } from "../ui/Button";
import { Card, CardHeader, CardTitle, CardDescription } from "../ui/Card";
import { Play, Square, Gauge, Flame, AlertOctagon, RefreshCw } from "lucide-react";
import { ATTACK_SCENARIOS } from "@/lib/constants";

interface SimulatorControlPanelProps {
  isRunning: boolean;
  currentTps: number;
  activeAttack: string | null;
  totalGenerated: number;
  onControl: (action: string, tps?: number, attack?: string) => Promise<void>;
}

export const SimulatorControlPanel: React.FC<SimulatorControlPanelProps> = ({
  isRunning,
  currentTps,
  activeAttack,
  totalGenerated,
  onControl,
}) => {
  const [sliderTps, setSliderTps] = useState(currentTps || 5);
  const [loadingAction, setLoadingAction] = useState<string | null>(null);

  const handleToggle = async () => {
    const action = isRunning ? "STOP" : "START";
    setLoadingAction(action);
    try {
      await onControl(action, sliderTps);
    } finally {
      setLoadingAction(null);
    }
  };

  const handleSpeedChange = async (newTps: number) => {
    setSliderTps(newTps);
    if (isRunning) {
      await onControl("SET_SPEED", newTps);
    }
  };

  const handleInjectAttack = async (attackId: string) => {
    setLoadingAction(attackId);
    try {
      await onControl("INJECT_ATTACK", sliderTps, attackId);
    } finally {
      setLoadingAction(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Control Console */}
      <Card className="border-blue-500/20 bg-gradient-to-br from-gray-900 via-gray-900 to-blue-950/20">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span
                className={`w-3 h-3 rounded-full ${
                  isRunning ? "bg-emerald-500 animate-ping" : "bg-gray-600"
                }`}
              />
              <CardTitle>Streaming Transaction Generator</CardTitle>
            </div>
            <CardDescription>
              Synthesize realistic cardholder profiles, geolocations, velocities, and simulated merchant networks.
            </CardDescription>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant={isRunning ? "danger" : "primary"}
              onClick={handleToggle}
              isLoading={loadingAction === (isRunning ? "STOP" : "START")}
            >
              {isRunning ? <Square className="w-4 h-4 mr-1.5" /> : <Play className="w-4 h-4 mr-1.5" />}
              {isRunning ? "Stop Stream" : "Start Live Stream"}
            </Button>
          </div>
        </div>

        {/* Speed Slider & Counters */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6 pt-6 border-t border-gray-800">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-400 font-medium">Throughput Pace (TPS)</span>
              <span className="text-xs font-bold text-blue-400 font-mono">{sliderTps} TPS</span>
            </div>
            <input
              type="range"
              min="1"
              max="50"
              value={sliderTps}
              onChange={(e) => handleSpeedChange(Number(e.target.value))}
              className="w-full h-1.5 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>

          <div className="bg-gray-950/60 border border-gray-800 rounded-xl p-3 text-center">
            <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Total Transactions</span>
            <p className="text-lg font-bold text-gray-100 font-mono mt-0.5">{totalGenerated.toLocaleString()}</p>
          </div>

          <div className="bg-gray-950/60 border border-gray-800 rounded-xl p-3 text-center">
            <span className="text-[10px] text-gray-500 uppercase tracking-wider font-semibold">Active Threat Wave</span>
            <p className="text-sm font-bold text-amber-400 font-mono mt-0.5 truncate">
              {activeAttack || "ORGANIC TRAFFIC"}
            </p>
          </div>
        </div>
      </Card>

      {/* Attack Scenarios Injector Grid */}
      <div>
        <h3 className="text-sm font-semibold text-gray-200 mb-3 flex items-center gap-2">
          <Flame className="w-4 h-4 text-red-400" />
          Inject Specialized Adversarial Fraud Attacks
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {ATTACK_SCENARIOS.map((scen) => (
            <div
              key={scen.id}
              className={`p-4 rounded-xl border bg-gray-900/80 transition-all ${
                activeAttack === scen.id
                  ? "border-red-500 ring-2 ring-red-500/20 bg-red-950/20"
                  : "border-gray-800 hover:border-gray-700"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-gray-100">{scen.name}</span>
                <span
                  className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                    scen.severity === "CRITICAL"
                      ? "bg-red-950/80 text-red-400 border border-red-500/30"
                      : "bg-amber-950/80 text-amber-400 border border-amber-500/30"
                  }`}
                >
                  {scen.severity}
                </span>
              </div>
              <p className="text-xs text-gray-400 mb-4 min-h-[36px]">{scen.description}</p>
              <Button
                variant="outline"
                size="sm"
                className="w-full"
                onClick={() => handleInjectAttack(scen.id)}
                isLoading={loadingAction === scen.id}
              >
                <AlertOctagon className="w-3.5 h-3.5 mr-1 text-red-400" />
                Inject Wave
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
