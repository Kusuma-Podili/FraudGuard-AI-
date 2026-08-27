"use client";

import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Settings, Shield, Sliders, Server, Save } from "lucide-react";

export default function SettingsPage() {
  const [reviewThreshold, setReviewThreshold] = useState("0.30");
  const [challengeThreshold, setChallengeThreshold] = useState("0.65");
  const [declineThreshold, setDeclineThreshold] = useState("0.85");
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = () => {
    setIsSaving(true);
    setTimeout(() => {
      setIsSaving(false);
      alert("Defense thresholds saved and synced across cluster nodes!");
    }, 600);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-gray-100 tracking-tight">System Settings & Governance</h1>
        <p className="text-xs text-gray-400 mt-1">
          Configure real-time decision thresholds, audit retention windows, and notification webhooks.
        </p>
      </div>

      {/* Decision Thresholds */}
      <Card className="space-y-6">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Sliders className="w-5 h-5 text-blue-400" />
            <div>
              <CardTitle>Autonomous Decision Thresholds</CardTitle>
              <CardDescription>Calibrate probability cutoff scores for automatic dispositions.</CardDescription>
            </div>
          </div>
          <Button size="sm" onClick={handleSave} isLoading={isSaving}>
            <Save className="w-3.5 h-3.5 mr-1" />
            Save Changes
          </Button>
        </CardHeader>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            label="Manual Review Threshold (Review)"
            value={reviewThreshold}
            onChange={(e) => setReviewThreshold(e.target.value)}
          />
          <Input
            label="3DS Step-Up Auth Threshold (Challenge)"
            value={challengeThreshold}
            onChange={(e) => setChallengeThreshold(e.target.value)}
          />
          <Input
            label="Instant Auto-Decline Threshold (Block)"
            value={declineThreshold}
            onChange={(e) => setDeclineThreshold(e.target.value)}
          />
        </div>
      </Card>

      {/* System Node Probes */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Server className="w-5 h-5 text-emerald-400" />
            <div>
              <CardTitle>Cluster Engine Nodes</CardTitle>
              <CardDescription>Health and latency metrics for gateway nodes.</CardDescription>
            </div>
          </div>
        </CardHeader>

        <div className="space-y-3">
          {[
            { name: "fraudguard-edge-us-east-1", status: "HEALTHY", latency: "3.2 ms", region: "US East (N. Virginia)" },
            { name: "fraudguard-edge-us-west-2", status: "HEALTHY", latency: "4.1 ms", region: "US West (Oregon)" },
            { name: "fraudguard-edge-eu-west-1", status: "HEALTHY", latency: "6.8 ms", region: "EU West (Frankfurt)" },
          ].map((node) => (
            <div
              key={node.name}
              className="p-3 bg-gray-950/60 border border-gray-800 rounded-xl flex items-center justify-between"
            >
              <div>
                <span className="text-xs font-semibold text-gray-200">{node.name}</span>
                <p className="text-[10px] text-gray-500">{node.region}</p>
              </div>
              <div className="text-right">
                <span className="text-[10px] font-bold text-emerald-400 px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-500/30">
                  {node.status}
                </span>
                <p className="text-[10px] text-gray-400 font-mono mt-0.5">{node.latency}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
