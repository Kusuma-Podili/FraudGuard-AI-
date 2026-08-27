"use client";

import React, { useState } from "react";
import { useRules } from "@/hooks/useRules";
import { RuleBuilder } from "@/components/rules/RuleBuilder";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { FraudRule } from "@/types";
import { Scale, CheckCircle2, XCircle, Play, ShieldAlert, Cpu } from "lucide-react";
import { getActionBadge } from "@/lib/utils";

export default function RulesPage() {
  const { rules, isLoading, createRule, dryRun, backtest, refresh } = useRules();
  const [activeTab, setActiveTab] = useState<"builder" | "list">("builder");

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-100 tracking-tight">Visual Rule Studio</h1>
          <p className="text-xs text-gray-400 mt-1">
            Author and deploy instant AST boolean rules combined with real-time ML score gating.
          </p>
        </div>

        {/* View Switcher */}
        <div className="flex items-center gap-2">
          <Button
            variant={activeTab === "builder" ? "primary" : "secondary"}
            size="sm"
            onClick={() => setActiveTab("builder")}
          >
            Rule Studio Builder
          </Button>
          <Button
            variant={activeTab === "list" ? "primary" : "secondary"}
            size="sm"
            onClick={() => setActiveTab("list")}
          >
            Active Rules ({rules.length})
          </Button>
        </div>
      </div>

      {activeTab === "builder" ? (
        <RuleBuilder onSaveRule={createRule} onDryRun={dryRun} />
      ) : (
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Configured Production Rules</CardTitle>
              <CardDescription>Rules executed sequentially by priority in sub-20ms inference gateway.</CardDescription>
            </div>
          </CardHeader>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-gray-300">
              <thead className="bg-gray-950/80 text-[11px] text-gray-400 uppercase tracking-wider border-b border-gray-800">
                <tr>
                  <th className="py-3 px-4 font-semibold">Priority</th>
                  <th className="py-3 px-4 font-semibold">Rule Code</th>
                  <th className="py-3 px-4 font-semibold">Name / Category</th>
                  <th className="py-3 px-4 font-semibold">Expression (Safe AST)</th>
                  <th className="py-3 px-4 font-semibold">Action</th>
                  <th className="py-3 px-4 font-semibold">Status</th>
                  <th className="py-3 px-4 font-semibold">Triggers</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {rules.map((r) => {
                  const badge = getActionBadge(r.action);
                  return (
                    <tr key={r.id || r.rule_code} className="hover:bg-gray-800/40 transition-colors">
                      <td className="py-3 px-4 font-mono font-bold text-gray-300">
                        #{r.priority}
                      </td>
                      <td className="py-3 px-4 font-mono font-bold text-blue-400">
                        {r.rule_code}
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-semibold text-gray-200">{r.name}</div>
                        <div className="text-[10px] text-gray-500">{r.category}</div>
                      </td>
                      <td className="py-3 px-4">
                        <code className="text-[11px] text-emerald-400 bg-gray-950 px-2 py-0.5 rounded border border-gray-800 font-mono">
                          {r.condition_expression}
                        </code>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${badge.className}`}>
                          {badge.label}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`inline-flex items-center gap-1 text-[11px] font-semibold ${
                            r.is_active ? "text-emerald-400" : "text-gray-500"
                          }`}
                        >
                          {r.is_active ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                          {r.is_active ? "ACTIVE" : "INACTIVE"}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-gray-300">
                        {r.total_triggered_count.toLocaleString()}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
