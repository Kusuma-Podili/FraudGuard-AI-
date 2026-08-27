export type RiskTier = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type DecisionAction = "ALLOW" | "REVIEW" | "CHALLENGE_3DS" | "DECLINE";

export interface TriggeredRuleInfo {
  rule_code: string;
  name: string;
  action: DecisionAction;
}

export interface TransactionRecord {
  id: string;
  transaction_id: string;
  card_id: string;
  cardholder_id: string;
  amount: number;
  currency: string;
  merchant_id: string;
  merchant_name?: string;
  merchant_category: string;
  entry_mode: string;
  card_type: string;
  card_network: string;
  latitude?: number;
  longitude?: number;
  country_code: string;
  device_fingerprint?: string;
  ip_address?: string;
  risk_score: number;
  decision_action: DecisionAction;
  risk_tier: RiskTier;
  triggered_rules: TriggeredRuleInfo[];
  model_breakdown: Record<string, number>;
  fraud_archetype: string;
  created_at: string;
}

export interface StreamTransactionEvent {
  event: string;
  transaction_id: string;
  card_id: string;
  amount: number;
  merchant_name: string;
  category: string;
  country: string;
  risk_score: number;
  decision_action: DecisionAction;
  risk_tier: RiskTier;
  is_anomaly: boolean;
  is_impossible_travel: boolean;
  fraud_archetype: string;
  latency_ms: number;
  timestamp: string;
}
