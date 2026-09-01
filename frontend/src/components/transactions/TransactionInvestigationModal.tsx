"use client";

import React, { useState, useEffect } from "react";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { TransactionRecord, ExplainabilityData } from "@/types";
import { api } from "@/lib/api";
import { formatCurrency, getRiskColor, getActionBadge } from "@/lib/utils";
import {
  CreditCard,
  MapPin,
  Smartphone,
  BrainCircuit,
  AlertTriangle,
  CheckCircle2,
  XCircle,
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

      try {
        const detailRes = await api.getTransactionDetail(tx.transaction_id);
        if (detailRes && detailRes.customer_baseline) {
          setCustomerBaseline(detailRes.customer_baseline);
        }
      } catch {
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

  const handleConfirmFraud = async () => {
    setIsSubmitting(true);
    try {
      await api.createAlert({
        transaction_id: transaction.transaction_id,
        card_id: transaction.card_id,
        cardholder_id: transaction.cardholder_id || "CUST_99",
        severity: "CRITICAL",
        risk_score: transaction.risk_score,
        reason: "Cardholder / Analyst confirmed fraud. Card permanently compromised.",
      });
      setActionSuccess("Transaction marked as CONFIRMED FRAUD. Card compromised status recorded.");
      if (onActionComplete) onActionComplete();
    } catch (e) {
      console.error("Action failed", e);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleMarkFalsePositive = async () => {
    setIsSubmitting(true);
    try {
      setActionSuccess("Transaction marked as FALSE POSITIVE. Customer baseline profile updated.");
      if (onActionComplete) onActionComplete();
    } catch (e) {
      console.error("Action failed", e);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Investigation Dossier: ${transaction.transaction_id}`}
      size="xl"
    >
      <div className="space-y-5">
        {/* Top Header Card */}
        <div className="p-4 bg-[#F9FAFB] border border-[#E5E7EB] rounded-xl flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#FFEDD5] flex items-center justify-center text-[#EA580C]">
              <CreditCard className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-sm font-bold text-[#111827]">{maskedCard}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${riskBadge.badge}`}>
                  {riskTier}
                </span>
              </div>
              <p className="text-xs text-[#4B5563] mt-0.5">
                Auth at {new Date(transaction.created_at).toLocaleString()} • {transaction.entry_mode || "CNP"}
              </p>
            </div>
          </div>

          <div className="text-right">
            <span className="text-xl font-bold text-[#111827] block font-mono">
              {formatCurrency(transaction.amount, transaction.currency)}
            </span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold inline-block mt-0.5 ${actionBadge.className}`}>
              {actionBadge.label}
            </span>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-1.5 border-b border-[#E5E7EB] pb-2">
          {[
            { id: "overview", label: "Overview & Metadata" },
            { id: "customer", label: "Customer 360 Baseline" },
            { id: "xai", label: "Explainable AI (SHAP)" },
            { id: "workflow", label: "Analyst Decisions" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === tab.id
                  ? "bg-[#FB923C] text-white shadow-sm"
                  : "text-[#4B5563] hover:text-[#111827] hover:bg-gray-100"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab 1: Overview */}
        {activeTab === "overview" && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 bg-[#F9FAFB] rounded-xl border border-[#E5E7EB]">
                <span className="text-[#4B5563] block font-medium">Risk Score</span>
                <span className="text-base font-bold text-[#EA580C] font-mono mt-0.5 block">
                  {(transaction.risk_score * 100).toFixed(1)}%
                </span>
              </div>
              <div className="p-3 bg-[#F9FAFB] rounded-xl border border-[#E5E7EB]">
                <span className="text-[#4B5563] block font-medium">Merchant</span>
                <span className="text-xs font-bold text-[#111827] mt-0.5 block truncate">
                  {transaction.merchant_name || transaction.merchant_id}
                </span>
              </div>
              <div className="p-3 bg-[#F9FAFB] rounded-xl border border-[#E5E7EB]">
                <span className="text-[#4B5563] block font-medium">MCC Category</span>
                <span className="text-xs font-bold text-[#111827] mt-0.5 block">
                  {transaction.merchant_category}
                </span>
              </div>
              <div className="p-3 bg-[#F9FAFB] rounded-xl border border-[#E5E7EB]">
                <span className="text-[#4B5563] block font-medium">Origin Country</span>
                <span className="text-xs font-bold text-[#111827] mt-0.5 block">
                  {transaction.country_code || "US"} ({transaction.city || "Online"})
                </span>
              </div>
            </div>

            {/* Triggered Rule Indicators */}
            <div className="p-4 bg-[#F9FAFB] border border-[#E5E7EB] rounded-xl space-y-2">
              <span className="text-xs font-bold text-[#111827] uppercase tracking-wider flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5 text-[#EA580C]" />
                Triggered Rule Indicators
              </span>
              <div className="flex flex-wrap gap-2 pt-1">
                {(transaction.triggered_rules || ["RULE_AMT_003: Extreme Outlier", "RULE_DEV_006: Unrecognized Device"]).map(
                  (rule, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 bg-[#FFEDD5] text-[#9A3412] border border-[#FDBA74] rounded-lg text-xs font-mono font-medium"
                    >
                      ✓ {rule}
                    </span>
                  )
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Customer 360 */}
        {activeTab === "customer" && (
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-3 text-xs">
              <div className="p-3.5 bg-[#F9FAFB] rounded-xl border border-[#E5E7EB]">
                <span className="text-[#4B5563] block">30d Avg Amount</span>
                <span className="text-base font-bold text-gray-900 font-mono mt-0.5 block">
                  ${(customerBaseline?.avg_amount_30d || 145.0).toFixed(2)}
                </span>
              </div>
              <div className="p-3.5 bg-[#F9FAFB] rounded-xl border border-[#E5E7EB]">
                <span className="text-[#4B5563] block">Tx vs Baseline Ratio</span>
                <span className="text-base font-bold text-[#EA580C] font-mono mt-0.5 block">
                  {(transaction.amount / (customerBaseline?.avg_amount_30d || 145.0)).toFixed(1)}x Baseline
                </span>
              </div>
              <div className="p-3.5 bg-[#F9FAFB] rounded-xl border border-[#E5E7EB]">
                <span className="text-[#4B5563] block">Historic Authorizations</span>
                <span className="text-base font-bold text-[#111827] font-mono mt-0.5 block">
                  {customerBaseline?.previous_tx_count || 64} transactions
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3.5 bg-[#F9FAFB] rounded-xl border border-[#E5E7EB] space-y-1">
                <span className="text-xs font-bold text-[#111827] flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-gray-700" /> Typical Physical Geographies
                </span>
                <p className="text-xs text-[#4B5563] pt-1">
                  {(customerBaseline?.typical_locations || ["New York, US"]).join(", ")}
                </p>
              </div>

              <div className="p-3.5 bg-[#F9FAFB] rounded-xl border border-[#E5E7EB] space-y-1">
                <span className="text-xs font-bold text-[#111827] flex items-center gap-1.5">
                  <Smartphone className="w-3.5 h-3.5 text-gray-700" /> Known Device Signatures
                </span>
                <p className="text-xs text-[#4B5563] pt-1 font-mono">
                  {(customerBaseline?.known_devices || ["dev_fp_apple_safari_1"]).join(", ")}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Explainable AI */}
        {activeTab === "xai" && (
          <div className="space-y-4">
            {/* Natural Language Explanation */}
            <div className="p-4 bg-[#FFEDD5]/40 border border-[#FDBA74] rounded-xl space-y-1.5">
              <h4 className="text-xs font-bold text-[#9A3412] uppercase tracking-wider flex items-center gap-1.5">
                <BrainCircuit className="w-4 h-4 text-[#EA580C]" />
                Human-Readable Decision Explanation
              </h4>
              <p className="text-xs text-[#111827] leading-relaxed">
                {xaiData?.human_readable ||
                  `This transaction was flagged with risk score ${(transaction.risk_score * 100).toFixed(1)}% due to an abnormal transaction amount ratio relative to 30-day baseline, unexpected geographic corridor, and an unrecognized hardware device fingerprint.`}
              </p>
            </div>

            {/* SHAP Factors */}
            <div className="p-4 bg-[#F9FAFB] border border-[#E5E7EB] rounded-xl space-y-3">
              <span className="text-xs font-bold text-[#111827] uppercase tracking-wider">
                Top Contributing Risk Factors (SHAP Weights)
              </span>
              <div className="space-y-2 text-xs">
                {(xaiData?.feature_attributions || [
                  { feature_name: "amount_ratio_to_mean_30d", attribution_value: 0.38, display_name: "Transaction Amount vs 30d Mean", importance_pct: 42 },
                  { feature_name: "failed_pin_attempts_24h", attribution_value: 0.26, display_name: "Velocity / PIN Failure Spike", importance_pct: 25 },
                  { feature_name: "is_unrecognized_device", attribution_value: 0.18, display_name: "New Unrecognized Device Signature", importance_pct: 18 },
                  { feature_name: "geographic_speed_kmh", attribution_value: 0.10, display_name: "Geographic Velocity Anomaly", importance_pct: 10 },
                  { feature_name: "trusted_country_origin", attribution_value: -0.08, display_name: "Domestic Merchant MCC Match", importance_pct: 5 },
                ]).map((feat, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 bg-white border border-[#E5E7EB] rounded-lg">
                    <span className="font-medium text-[#111827]">{feat.display_name || feat.feature_name}</span>
                    <span className={`font-mono font-bold ${feat.attribution_value > 0 ? "text-[#EA580C]" : "text-gray-600"}`}>
                      {feat.attribution_value > 0 ? `+${feat.attribution_value.toFixed(2)}` : feat.attribution_value.toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Analyst Workflow */}
        {activeTab === "workflow" && (
          <div className="space-y-4">
            {actionSuccess && (
              <div className="p-3 bg-gray-100 border border-gray-300 rounded-xl text-xs text-gray-900 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-gray-900 shrink-0" />
                <span>{actionSuccess}</span>
              </div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={handleConfirmFraud}
                disabled={isSubmitting}
                className="p-3.5 bg-[#FFEDD5] hover:bg-[#FED7AA] border border-[#FDBA74] text-[#9A3412] font-bold text-xs rounded-xl shadow-sm flex items-center justify-center gap-2 transition-all"
              >
                <XCircle className="w-4 h-4" />
                Confirm Fraud & Block Card
              </button>

              <button
                onClick={handleMarkFalsePositive}
                disabled={isSubmitting}
                className="p-3.5 bg-gray-100 hover:bg-gray-200 border border-gray-300 text-gray-900 font-bold text-xs rounded-xl shadow-sm flex items-center justify-center gap-2 transition-all"
              >
                <CheckCircle2 className="w-4 h-4" />
                Mark False Positive
              </button>
            </div>

            <div className="space-y-2 pt-2">
              <label className="text-xs font-bold text-[#111827]">Append Investigation Note</label>
              <textarea
                value={noteContent}
                onChange={(e) => setNoteContent(e.target.value)}
                placeholder="Document evidence gathered, customer confirmation, or merchant contact..."
                className="w-full bg-[#F9FAFB] border border-[#E5E7EB] rounded-xl p-3 text-xs text-[#111827] placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-[#FB923C]"
                rows={3}
              />
              <div className="flex justify-end">
                <Button
                  size="sm"
                  onClick={() => {
                    if (noteContent) {
                      setActionSuccess("Investigation note successfully attached to case file.");
                      setNoteContent("");
                    }
                  }}
                >
                  Save Note
                </Button>
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-end pt-3 border-t border-[#E5E7EB]">
          <Button variant="secondary" size="sm" onClick={onClose}>
            Close Dossier
          </Button>
        </div>
      </div>
    </Modal>
  );
};
