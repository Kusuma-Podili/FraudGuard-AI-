"use client";

import React, { useState, useEffect } from "react";
import { SimulatorControlPanel } from "@/components/simulator/SimulatorControlPanel";
import { api } from "@/lib/api";
import { Flame } from "lucide-react";

export default function SimulatorPage() {
  const [simulatorState, setSimulatorState] = useState({
    is_running: false,
    target_tps: 5,
    active_attack: null,
    total_generated: 0,
  });

  useEffect(() => {
    async function loadStatus() {
      try {
        const data = await api.getSimulatorStatus();
        setSimulatorState(data);
      } catch (e) {
        console.error(e);
      }
    }
    loadStatus();
    const interval = setInterval(loadStatus, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleControl = async (action: string, tps?: number, attack?: string) => {
    const res = await api.controlSimulator(action, tps, attack);
    setSimulatorState(res);
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center gap-2">
        <Flame className="w-6 h-6 text-red-500" />
        <div>
          <h1 className="text-2xl font-bold text-gray-100 tracking-tight">Adversarial Stream Simulator</h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Synthetic transaction sandbox with controllable throughput and multi-archetype attack injectors.
          </p>
        </div>
      </div>

      <SimulatorControlPanel
        isRunning={simulatorState.is_running}
        currentTps={simulatorState.target_tps}
        activeAttack={simulatorState.active_attack}
        totalGenerated={simulatorState.total_generated}
        onControl={handleControl}
      />
    </div>
  );
}
