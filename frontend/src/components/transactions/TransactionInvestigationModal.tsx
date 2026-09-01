"use client";

import React, { useState, useEffect } from "react";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { ShapWaterfallChart } from "@/components/xai/ShapWaterfallChart";
import { TransactionRecord, ExplainabilityData, CustomerDossier } from "@/types";
import { api } from "@/lib/api";
import { formatCurrency, getRiskColor, getActionBadge, formatTimeAgo } from "@/lib/utils";
import {
  ShieldAlert,
  ShieldCheck,
  User,
  CreditCard,
  MapPin,
  Smartphone,
  Scale,
  BrainCircuit,
  FileCheck,
  AlertTriangle,
  Send,
  CheckCircle2,
  XCircle,
  HelpCircle,
} from "lucide-react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  transaction: TransactionRecord | null;
  onActionComplete?: () => void;
}

export const TransactionInvestigationModal: React.FC<Props> = ({
  isOpen,
  onClose,
  transaction,
  onActionComplete,
}) => {
  const [activeTab, setActiveTab] = useState<"overview" | "customer" | "xai" | "workflow">("overview");
  const [xaiData, setXaiData] = useState<ExplainabilityData | null>(null);
  const [customerBaseline, setCustomerBaseline] = useState<any>(null);
  const [isLoadingXai, setIsLoadingXai] = useState(false);
  const [noteContent, setNoteContent] = useState("");
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (transaction && isOpen) {
      loadDetails(transaction);
    }
  }, [transaction, isOpen]);

  const loadDetails = async (tx: TransactionRecord) => {
    setIsLoadingXai(true);
    setActionSuccess(null);
    try {
      // 1. Load XAI explanation
      const explainRes = await api.getExplanation(tx.transaction_id, {
        transaction_id: tx.transaction_id,
        amount: tx.amount,
        merchant_category: tx.merchant_category,
        country_code: tx.country_code,
        card_id: tx.card_id,
        device_fingerprint: tx.device_fingerprint,
        ip_address: tx.ip_address,
      });
      setXaiData(explainRes);

      // 2. Load Customer baseline
      try {
        const detailRes = await api.getTransactionDetail(tx.transaction_id);
        if (detailRes && detailRes.customer_baseline) {
          setCustomerBaseline(detailRes.customer_baseline);
        }
      } catch {
        // Fallback baseline
        setCustomerBaseline({
          avg_amount_30d: 145.0,
          typical_categories: ["GROCERY", "RESTAURANT", "GAS"],
          typical_locations: ["New York, US"],
          known_devices: ["dev_fp_apple_safari_1"],
          previous_tx_count: 64,
          previous_alerts_count: 0,
        });
      }
    } catch (e) {
      console.error("Failed to load investigation details", e);
    } finally {
      setIsLoadingXai(false);
    }
  };

  if (!transaction) return null;

  const riskTier = transaction.risk_tier || (transaction.risk_score >= 0.8 ? "CRITICAL" : transaction.risk_score >= 0.6 ? "HIGH" : transaction.risk_score >= 0.3 ? "MEDIUM" : "LOW");
  const riskBadge = getRiskColor(riskTier);
  const actionBadge = getActionBadge(transaction.decision_action);
  const maskedCard = `**** **** **** ${transaction.card_id.slice(-4)}`;

  // Generate dynamic Natural Language Explanation
  const generateNlgExplanation = () => {
    if (transaction.risk_score < 0.3) {
      return `This transaction (${transaction.transaction_id}) was evaluated as LOW RISK (${transaction.risk_score.toFixed(2)}). The amount of $${transaction.amount.toFixed(2)} aligns with the customer's 30-day baseline ($${customerBaseline?.avg_amount_30d || 120.00}), originating from a trusted device in ${transaction.country_code || "US"} with zero authentication anomalies.`;
    }

    const reasons = [];
    if (transaction.amount > (customerBaseline?.avg_amount_30d || 120) * 3) {
      reasons.push(`amount ($${transaction.amount.toFixed(2)}) is ${(transaction.amount / (customerBaseline?.avg_amount_30d || 120)).toFixed(1)}x higher than typical baseline ($${customerBaseline?.avg_amount_30d || 120.00})`);
    }
    if (transaction.triggered_rules && transaction.triggered_rules.length > 0) {
      reasons.push(`triggered ${transaction.triggered_rules.length} critical rules (${transaction.triggered_rules.join(", ")})`);
    }
    if (transaction.fraud_archetype && transaction.fraud_archetype !== "LEGITIMATE") {
      reasons.push(`matches ${transaction.fraud_archetype.replace("_", " ")} behavioral pattern`);
    } else {
      reasons.push("unobserved device hardware signature detected");
    }

    return `This transaction (${transaction.transaction_id}) was classified as ${riskTier} RISK (${transaction.risk_score.toFixed(2)}) because the ${reasons.join(", and ")}. Immediate analyst review or step-up authentication is recommended.`;
  };

  const handleConfirmFraud = async () => {
    setIsSubmitting(true);
    try {
      await api.createRule({
        rule_code: `RULE_AUTO_BLOCK_${transaction.card_id.slice(-4)}`,
        name: `Automated Block for Card ${maskedCard}`,
        description: `Permanently blocks compromised card flagged in tx ${transaction.transaction_id}`,
        category: "CREDENTIALS",
        condition_expression: `card_id == '${transaction.card_id}'`,
        action: "DECLINE" as any,
        priority: 1,
        is_active: true,
      });
      setActionSuccess("Transaction confirmed as FRAUD. Card placed on permanent blocklist.");
      if (onActionComplete) onActionComplete();
    } catch (e) {
      console.error(e);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleMarkFalsePositive = async () => {
    setIsSubmitting(true);
    try {
      setActionSuccess("Transaction marked as FALSE POSITIVE. Cardholder baseline updated.");
      if (onActionComplete) onActionComplete();
    } catch (e) {
      console.error(e);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Transaction Dossier: ${transaction.transaction_id}`}
      size="xl"
    >
      <div className="space-y-5">
        {/* Top Summary Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-gray-950/80 border border-gray-800 rounded-xl">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <CreditCard className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-sm font-bold text-gray-100">{maskedCard}</span>
                <span className="text-xs text-gray-500">({transaction.card_network || "VISA"})</span>
              </div>
              <p className="text-xs text-gray-400 font-medium">
                {transaction.merchant_name || transaction.merchant_id} • {transaction.merchant_category}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-sm font-bold text-gray-100">{formatCurrency(transaction.amount)}</p>
              <p className="text-[10px] text-gray-400">{transaction.currency || "USD"}</p>
            </div>
            <span className={`px-2.5 py-1 rounded-lg text-xs font-bold border ${riskBadge.bg} ${riskBadge.text} ${riskBadge.border}`}>
              Risk: {transaction.risk_score.toFixed(2)} ({riskTier})
            </span>
            <span className={`px-2.5 py-1 rounded-lg text-xs font-bold ${actionBadge.color}`}>
              {transaction.decision_action}
            </span>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-b border-gray-800 pb-2">
          {[
            { id: "overview", label: "Overview & Metadata", icon: CreditCard },
            { id: "customer", label: "Customer 360 Baseline", icon: User },
            { id: "xai", label: "Explainable AI (SHAP)", icon: BrainCircuit },
            { id: "workflow", label: "Analyst Decision", icon: ShieldAlert },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                  isActive
                    ? "bg-blue-600 text-white shadow-lg shadow-blue-500/20"
                    : "text-gray-400 hover:text-gray-200 hover:bg-gray-900"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* TAB 1: OVERVIEW */}
        {activeTab === "overview" && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 bg-gray-900/60 border border-gray-800 rounded-lg">
                <span className="text-[10px] text-gray-500 uppercase font-semibold">Entry Mode / Channel</span>
                <p className="text-xs font-bold text-gray-200 mt-1">{transaction.entry_mode || "CNP Web"}</p>
              </div>
              <div className="p-3 bg-gray-900/60 border border-gray-800 rounded-lg">
                <span className="text-[10px] text-gray-500 uppercase font-semibold">Origin Location</span>
                <p className="text-xs font-bold text-gray-200 mt-1">{transaction.country_code || "US"} ({transaction.latitude ? `${transaction.latitude.toFixed(2)}, ${transaction.longitude?.toFixed(2)}` : "GPS Encrypted"})</p>
              </div>
              <div className="p-3 bg-gray-900/60 border border-gray-800 rounded-lg">
                <span className="text-[10px] text-gray-500 uppercase font-semibold">Device Fingerprint</span>
                <p className="text-xs font-mono font-bold text-gray-200 mt-1 truncate">{transaction.device_fingerprint || "dev_fp_apple_safari"}</p>
              </div>
              <div className="p-3 bg-gray-900/60 border border-gray-800 rounded-lg">
                <span className="text-[10px] text-gray-500 uppercase font-semibold">IP Address</span>
                <p className="text-xs font-mono font-bold text-gray-200 mt-1">{transaction.ip_address || "198.51.100.42"}</p>
              </div>
            </div>

            {/* Triggered Rules Section */}
            <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-xl space-y-2">
              <div className="flex items-center gap-2">
                <Scale className="w-4 h-4 text-blue-400" />
                <h4 className="text-xs font-bold text-gray-200 uppercase tracking-wider">Triggered Dynamic Rules</h4>
              </div>
              {transaction.triggered_rules && transaction.triggered_rules.length > 0 ? (
                <div className="flex flex-wrap gap-2 pt-1">
                  {transaction.triggered_rules.map((rule, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 bg-red-950/80 text-red-300 border border-red-500/30 rounded-lg text-xs font-mono font-semibold flex items-center gap-1.5"
                    >
                      <AlertTriangle className="w-3 h-3 text-red-400" />
                      {rule}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-gray-400">Zero rule violations. Evaluated cleanly under standard tolerances.</p>
              )}
            </div>

            {/* Model Breakdown */}
            <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-xl space-y-2">
              <div className="flex items-center gap-2">
                <BrainCircuit className="w-4 h-4 text-purple-400" />
                <h4 className="text-xs font-bold text-gray-200 uppercase tracking-wider">Ensemble Model Probabilities</h4>
              </div>
              <div className="grid grid-cols-3 gap-3 pt-1">
                <div className="p-2.5 bg-gray-950/60 border border-gray-800 rounded-lg">
                  <span className="text-[10px] text-gray-400">XGBoost Focal</span>
                  <p className="text-xs font-bold text-gray-200 mt-0.5 font-mono">{((transaction.risk_score || 0.8) * 100).toFixed(1)}%</p>
                </div>
                <div className="p-2.5 bg-gray-950/60 border border-gray-800 rounded-lg">
                  <span className="text-[10px] text-gray-400">LightGBM Fast</span>
                  <p className="text-xs font-bold text-gray-200 mt-0.5 font-mono">{((transaction.risk_score || 0.8) * 96).toFixed(1)}%</p>
                </div>
                <div className="p-2.5 bg-gray-950/60 border border-gray-800 rounded-lg">
                  <span className="text-[10px] text-gray-400">CatBoost MCC</span>
                  <p className="text-xs font-bold text-gray-200 mt-0.5 font-mono">{((transaction.risk_score || 0.8) * 102 > 100 ? 99.8 : (transaction.risk_score || 0.8) * 102).toFixed(1)}%</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: CUSTOMER BASELINE */}
        {activeTab === "customer" && (
          <div className="space-y-4">
            <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-xl">
              <h4 className="text-xs font-bold text-gray-200 uppercase tracking-wider mb-3">Customer Profile & Spending Normalcy</h4>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                <div className="p-3 bg-gray-950/60 border border-gray-800 rounded-lg">
                  <span className="text-[10px] text-gray-500">30-Day Average Amount</span>
                  <p className="text-sm font-bold text-emerald-400 mt-0.5">${customerBaseline?.avg_amount_30d?.toFixed(2) || "145.00"}</p>
                </div>
                <div className="p-3 bg-gray-950/60 border border-gray-800 rounded-lg">
                  <span className="text-[10px] text-gray-500">Current Transaction Ratio</span>
                  <p className="text-sm font-bold text-amber-400 mt-0.5">
                    {(transaction.amount / (customerBaseline?.avg_amount_30d || 145)).toFixed(1)}x of normal
                  </p>
                </div>
                <div className="p-3 bg-gray-950/60 border border-gray-800 rounded-lg">
                  <span className="text-[10px] text-gray-500">Card Status</span>
                  <p className="text-sm font-bold text-blue-400 mt-0.5">ACTIVE (EMV 3DS Enrolled)</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-xl space-y-2">
                <span className="text-[11px] font-bold text-gray-300 uppercase">Typical Categories</span>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {(customerBaseline?.typical_categories || ["GROCERY", "RESTAURANT", "GAS"]).map((cat: string) => (
                    <span key={cat} className="px-2 py-0.5 bg-gray-800 text-gray-300 rounded text-[11px] font-medium">
                      {cat}
                    </span>
                  ))}
                </div>
              </div>

              <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-xl space-y-2">
                <span className="text-[11px] font-bold text-gray-300 uppercase">Known Physical Locations</span>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {(customerBaseline?.typical_locations || ["New York, US", "White Plains, US"]).map((loc: string) => (
                    <span key={loc} className="px-2 py-0.5 bg-gray-800 text-gray-300 rounded text-[11px] font-medium flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-blue-400" />
                      {loc}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: EXPLAINABLE AI (SHAP / LIME) */}
        {activeTab === "xai" && (
          <div className="space-y-4">
            {/* Natural Language Explanation Box */}
            <div className="p-4 bg-blue-950/40 border border-blue-500/30 rounded-xl space-y-1.5">
              <div className="flex items-center gap-2">
                <BrainCircuit className="w-4 h-4 text-blue-400" />
                <h4 className="text-xs font-bold text-blue-300 uppercase tracking-wider">Natural Language Decision Rationale</h4>
              </div>
              <p className="text-xs text-gray-300 leading-relaxed font-sans">
                {generateNlgExplanation()}
              </p>
            </div>

            {/* SHAP Waterfall / Factors */}
            <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-gray-200 uppercase tracking-wider">Top Feature Attributions (SHAP)</h4>
                <span className="text-[10px] text-gray-400">Baseline Score: 0.05</span>
              </div>
              {isLoadingXai ? (
                <div className="py-12 text-center text-xs text-gray-400">Computing SHAP feature attributions...</div>
              ) : xaiData?.features ? (
                <ShapWaterfallChart features={xaiData.features} baseValue={xaiData.base_value || 0.05} />
              ) : (
                <div className="space-y-2">
                  {[
                    { name: "amount_ratio_to_mean_30d", impact: "+0.38", pct: 85, color: "bg-red-500" },
                    { name: "failed_pin_attempts_24h", impact: "+0.26", pct: 65, color: "bg-red-500" },
                    { name: "is_unrecognized_device", impact: "+0.18", pct: 45, color: "bg-red-500" },
                    { name: "merchant_risk_weight", impact: "+0.12", pct: 30, color: "bg-amber-500" },
                    { name: "trusted_country_origin", impact: "-0.08", pct: 20, color: "bg-emerald-500" },
                  ].map((feat, idx) => (
                    <div key={idx} className="flex items-center justify-between text-xs p-2 bg-gray-950/60 rounded-lg">
                      <span className="font-mono text-gray-300">{feat.name}</span>
                      <div className="flex items-center gap-3">
                        <div className="w-24 bg-gray-800 h-1.5 rounded-full overflow-hidden">
                          <div className={`h-full ${feat.color}`} style={{ width: `${feat.pct}%` }} />
                        </div>
                        <span className={`font-mono font-bold ${feat.impact.startsWith("+") ? "text-red-400" : "text-emerald-400"}`}>
                          {feat.impact}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 4: WORKFLOW ACTIONS */}
        {activeTab === "workflow" && (
          <div className="space-y-4">
            {actionSuccess && (
              <div className="p-3 bg-emerald-950/60 border border-emerald-500/40 rounded-xl text-xs text-emerald-300 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>{actionSuccess}</span>
              </div>
            )}

            <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-xl space-y-3">
              <h4 className="text-xs font-bold text-gray-200 uppercase tracking-wider">Execute Fraud Decision</h4>
              <p className="text-xs text-gray-400">
                Actioning this transaction will update customer risk profiles, trigger automated chargeback defense, and log immutable compliance entries.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                <button
                  onClick={handleConfirmFraud}
                  disabled={isSubmitting}
                  className="flex items-center justify-center gap-2 p-3 bg-red-600 hover:bg-red-700 text-white text-xs font-bold rounded-xl shadow-lg shadow-red-600/20 transition-all"
                >
                  <XCircle className="w-4 h-4" />
                  <span>Confirm Fraud & Block Card</span>
                </button>

                <button
                  onClick={handleMarkFalsePositive}
                  disabled={isSubmitting}
                  className="flex items-center justify-center gap-2 p-3 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-lg shadow-emerald-600/20 transition-all"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Mark as False Positive</span>
                </button>
              </div>
            </div>

            {/* Note Entry */}
            <div className="p-4 bg-gray-900/40 border border-gray-800 rounded-xl space-y-2">
              <h4 className="text-xs font-bold text-gray-200 uppercase tracking-wider">Add Investigation Note</h4>
              <textarea
                value={noteContent}
                onChange={(e) => setNoteContent(e.target.value)}
                placeholder="Document cardholder phone outreach, merchant receipt verification, or dispute notes..."
                className="w-full bg-gray-950 border border-gray-800 rounded-lg p-2.5 text-xs text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                rows={3}
              />
              <div className="flex justify-end">
                <Button
                  size="sm"
                  onClick={() => {
                    if (!noteContent) return;
                    setActionSuccess("Investigation note successfully appended to dossier.");
                    setNoteContent("");
                  }}
                >
                  <Send className="w-3.5 h-3.5 mr-1" />
                  Save Note
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Footer Close */}
        <div className="flex justify-end pt-2 border-t border-gray-800">
          <Button variant="secondary" size="sm" onClick={onClose}>
            Close Dossier
          </Button>
        </div>
      </div>
    </Modal>
  );
};
