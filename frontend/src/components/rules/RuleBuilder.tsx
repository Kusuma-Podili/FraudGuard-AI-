"use client";

import React, { useState } from "react";
import { Button } from "../ui/Button";
import { Input } from "../ui/Input";
import { Select } from "../ui/Select";
import { Card, CardHeader, CardTitle, CardDescription } from "../ui/Card";
import { Play, Sparkles, AlertCircle, CheckCircle2 } from "lucide-react";
import { RuleDryRunResult } from "@/types";

interface RuleBuilderProps {
  onSaveRule: (rule: any) => Promise<void>;
  onDryRun: (condition: string, sample: any) => Promise<RuleDryRunResult>;
}

export const RuleBuilder: React.FC<RuleBuilderProps> = ({ onSaveRule, onDryRun }) => {
  const [ruleCode, setRuleCode] = useState("RULE_CUSTOM_01");
  const [ruleName, setRuleName] = useState("High Velocity Electronics Surge");
  const [category, setCategory] = useState("VELOCITY");
  const [action, setAction] = useState("DECLINE");
  const [priority, setPriority] = useState(15);
  const [condition, setCondition] = useState("amount > 1500.0 AND velocity_1h >= 3 AND merchant_category == 'ELECTRONICS'");
  const [isDryRunning, setIsDryRunning] = useState(false);
  const [dryRunResult, setDryRunResult] = useState<RuleDryRunResult | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const samplePayload = {
    amount: 2200.0,
    velocity_1h: 4,
    velocity_24h: 7,
    merchant_category: "ELECTRONICS",
    country_code: "US",
    failed_pin_attempts_24h: 0,
    distance_from_home_km: 12.5,
    is_impossible_travel: false,
    travel_velocity_kmh: 0.0,
    amount_ratio_to_mean_30d: 2.8,
  };

  const handleDryRun = async () => {
    setIsDryRunning(true);
    try {
      const res = await onDryRun(condition, samplePayload);
      setDryRunResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setIsDryRunning(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onSaveRule({
        rule_code: ruleCode,
        name: ruleName,
        category,
        action,
        priority: Number(priority),
        condition_expression: condition,
        is_active: true,
      });
      alert("Rule created and compiled successfully!");
    } catch (e: any) {
      alert("Error saving rule: " + e.message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Card className="space-y-6">
      <CardHeader>
        <div>
          <CardTitle>AST Visual Rule Studio</CardTitle>
          <CardDescription>
            Author high-performance boolean logic expressions evaluated in microseconds.
          </CardDescription>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" onClick={handleDryRun} isLoading={isDryRunning}>
            <Play className="w-3.5 h-3.5 mr-1 text-emerald-400" />
            Dry-Run Test
          </Button>
          <Button variant="primary" size="sm" onClick={handleSave} isLoading={isSaving}>
            <Sparkles className="w-3.5 h-3.5 mr-1" />
            Deploy Rule
          </Button>
        </div>
      </CardHeader>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Input label="Rule Code" value={ruleCode} onChange={(e) => setRuleCode(e.target.value)} />
        <Input label="Rule Name" value={ruleName} onChange={(e) => setRuleName(e.target.value)} />
        <Select
          label="Category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          options={[
            { value: "VELOCITY", label: "Velocity Spike" },
            { value: "AMOUNT", label: "Amount Outlier" },
            { value: "GEO", label: "Impossible Travel / Geo" },
            { value: "CREDENTIALS", label: "Failed Authentication" },
            { value: "MERCHANT", label: "Merchant Risk" },
          ]}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Select
          label="Action on Trigger"
          value={action}
          onChange={(e) => setAction(e.target.value)}
          options={[
            { value: "DECLINE", label: "DECLINE (Instant Rejection)" },
            { value: "CHALLENGE_3DS", label: "CHALLENGE_3DS (Step-Up Auth)" },
            { value: "REVIEW", label: "REVIEW (Queue Investigation)" },
          ]}
        />
        <Input
          label="Priority (Lower number = Higher precedence)"
          type="number"
          value={priority}
          onChange={(e) => setPriority(Number(e.target.value))}
        />
      </div>

      {/* Condition Editor */}
      <div>
        <label className="block text-xs font-medium text-gray-300 mb-1.5">
          Boolean Expression Condition (Safe AST)
        </label>
        <textarea
          rows={3}
          value={condition}
          onChange={(e) => setCondition(e.target.value)}
          className="w-full bg-gray-950/90 border border-gray-800 rounded-lg p-3 font-mono text-xs text-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <p className="text-[11px] text-gray-500 mt-1">
          Supported variables: <code>amount</code>, <code>velocity_1h</code>, <code>velocity_24h</code>, <code>distance_from_home_km</code>, <code>travel_velocity_kmh</code>, <code>is_impossible_travel</code>, <code>failed_pin_attempts_24h</code>, <code>merchant_category</code>
        </p>
      </div>

      {/* Dry Run Outcome Panel */}
      {dryRunResult && (
        <div
          className={`p-4 rounded-xl border ${
            dryRunResult.is_triggered
              ? "bg-red-950/30 border-red-500/40 text-red-300"
              : "bg-emerald-950/30 border-emerald-500/40 text-emerald-300"
          }`}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {dryRunResult.is_triggered ? (
                <AlertCircle className="w-5 h-5 text-red-400" />
              ) : (
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              )}
              <span className="text-xs font-bold uppercase tracking-wider">
                {dryRunResult.is_triggered ? "Rule Triggered Match!" : "Rule Did Not Trigger (Pass)"}
              </span>
            </div>
            <span className="font-mono text-xs text-gray-400">
              Evaluated in <strong>{dryRunResult.latency_microseconds} µs</strong>
            </span>
          </div>
        </div>
      )}
    </Card>
  );
};
