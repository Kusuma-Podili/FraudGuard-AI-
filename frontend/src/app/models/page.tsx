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
          <h1 className="text-2xl font-bold text-gray-100 tracking-tight">MLOps & Model Governance Registry</h1>
          <p className="text-xs text-gray-400 mt-1">
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
                isChampion ? "border-blue-500 bg-gradient-to-b from-blue-950/20 to-gray-900" : ""
              }`}
            >
              {isChampion && (
                <div className="absolute top-4 right-4 flex items-center gap-1 px-2 py-0.5 rounded-full bg-blue-500 text-white text-[10px] font-bold">
                  <Trophy className="w-3 h-3" />
                  CHAMPION
                </div>
              )}

              <div>
                <p className="text-xs font-mono text-gray-400">{m.model_id}</p>
                <h3 className="text-base font-bold text-gray-100 mt-1">{m.name}</h3>
                <p className="text-xs text-gray-400 mt-0.5">{m.algorithm_type}</p>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-3 gap-2 my-4 p-3 bg-gray-950/60 rounded-xl border border-gray-800 text-center">
                <div>
                  <span className="text-[10px] text-gray-500 uppercase">ROC-AUC</span>
                  <p className="text-sm font-bold text-blue-400 mt-0.5 font-mono">{m.roc_auc.toFixed(3)}</p>
                </div>
                <div>
                  <span className="text-[10px] text-gray-500 uppercase">PR-AUC</span>
                  <p className="text-sm font-bold text-emerald-400 mt-0.5 font-mono">{m.pr_auc.toFixed(3)}</p>
                </div>
                <div>
                  <span className="text-[10px] text-gray-500 uppercase">P99 Latency</span>
                  <p className="text-sm font-bold text-gray-200 mt-0.5 font-mono">{m.p99_latency_ms.toFixed(1)}ms</p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-gray-800">
                <span className="text-xs text-gray-400">Traffic: <strong className="text-gray-200 font-mono">{m.traffic_percentage}%</strong></span>
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

          <Card>
            <CardHeader>
              <div>
                <CardTitle>Global Feature Importance</CardTitle>
                <CardDescription>TreeSHAP gain distribution across model input features.</CardDescription>
              </div>
            </CardHeader>
            <div className="space-y-3">
              {(liveMetrics.feature_importances || []).map((f: any, idx: number) => (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-300 font-semibold">{f.feature}</span>
                    <span className="text-blue-400 font-mono font-bold">{(f.importance * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-gray-950 rounded-full h-2 overflow-hidden border border-gray-800">
                    <div
                      className="bg-blue-500 h-full rounded-full"
                      style={{ width: `${f.importance * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
