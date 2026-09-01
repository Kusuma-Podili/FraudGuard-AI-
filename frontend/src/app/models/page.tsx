"use client";

import React from "react";
import { useModels } from "@/hooks/useModels";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { RocCurveChart } from "@/components/charts/RocCurveChart";
import { BrainCircuit, Trophy, ArrowUpRight, Cpu, ShieldCheck, Activity } from "lucide-react";

export default function ModelsPage() {
  const { models, liveMetrics, isLoading, promoteModel } = useModels();

  const handlePromote = async (modelId: string) => {
    try {
      await promoteModel(modelId);
      alert("Model promoted to Champion!");
    } catch (e: any) {
      alert("Failed to promote: " + e.message);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[#29332F] tracking-tight">MLOps & Model Governance Registry</h1>
          <p className="text-xs text-[#69736E] mt-1">
            Champion/Challenger deployment framework, tree ensembles, deep autoencoders, and graph syndicates.
          </p>
        </div>
      </div>

      {/* Model Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {models.map((m) => {
          const isChampion = m.status === "CHAMPION";
          return (
            <Card
              key={m.id || m.model_id}
              className={`relative ${
                isChampion ? "border-[#5F8F83] bg-[#FFFDFC]" : ""
              }`}
            >
              {isChampion && (
                <div className="absolute top-4 right-4 flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#5F8F83] text-white text-[10px] font-bold">
                  <Trophy className="w-3 h-3" />
                  CHAMPION
                </div>
              )}

              <div>
                <p className="text-xs font-mono text-[#69736E]">{m.model_id}</p>
                <h3 className="text-base font-bold text-[#29332F] mt-1">{m.name}</h3>
                <p className="text-xs text-[#69736E] mt-0.5">{m.algorithm_type} • v{m.version}</p>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-3 gap-2 my-4 p-3 bg-[#F7F4EF] rounded-xl border border-[#E5DED5] text-center">
                <div>
                  <span className="text-[10px] text-[#929A95] uppercase font-medium">ROC-AUC</span>
                  <p className="text-sm font-bold text-[#5F8F83] mt-0.5 font-mono">{m.roc_auc.toFixed(3)}</p>
                </div>
                <div>
                  <span className="text-[10px] text-[#929A95] uppercase font-medium">PR-AUC</span>
                  <p className="text-sm font-bold text-[#35604B] mt-0.5 font-mono">{m.pr_auc.toFixed(3)}</p>
                </div>
                <div>
                  <span className="text-[10px] text-[#929A95] uppercase font-medium">P99 Latency</span>
                  <p className="text-sm font-bold text-[#29332F] mt-0.5 font-mono">{m.p99_latency_ms.toFixed(1)}ms</p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-[#E5DED5]">
                <span className="text-xs text-[#69736E]">Traffic: <strong className="text-[#29332F] font-mono">{m.traffic_percentage}%</strong></span>
                {!isChampion && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePromote(m.id || m.model_id)}
                  >
                    Promote to Champion
                  </Button>
                )}
              </div>
            </Card>
          );
        })}
      </div>

      {/* Live MLOps Governance Panel */}
      {liveMetrics && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <div>
                <CardTitle>ROC-AUC Discrimination Curve</CardTitle>
                <CardDescription>Live true positive vs false positive curve across thresholds.</CardDescription>
              </div>
            </CardHeader>
            <RocCurveChart data={liveMetrics.roc_curve || []} />
          </Card>

          <Card className="space-y-4 p-5">
            <div>
              <CardTitle>Inference Health Telemetry</CardTitle>
              <CardDescription>Real-time gateway SLA monitoring and prediction speed.</CardDescription>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3.5 bg-[#F7F4EF] rounded-xl border border-[#E5DED5]">
                <span className="text-[#69736E] block">Active Model In Production</span>
                <p className="text-sm font-bold text-[#5F8F83] mt-1">Meta-Ensemble Hybrid</p>
              </div>
              <div className="p-3.5 bg-[#F7F4EF] rounded-xl border border-[#E5DED5]">
                <span className="text-[#69736E] block">P99 Inference Guarantee</span>
                <p className="text-sm font-bold text-[#35604B] mt-1">&lt; 20.0 ms SLA</p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
