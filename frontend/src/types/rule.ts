export interface FraudRule {
  id: string;
  rule_code: string;
  name: string;
  description?: string;
  category: "VELOCITY" | "AMOUNT" | "GEO" | "MERCHANT" | "CREDENTIALS";
  condition_expression: string;
  action: "ALLOW" | "REVIEW" | "CHALLENGE_3DS" | "DECLINE" | "TAG_SUSPICIOUS";
  priority: number;
  is_active: boolean;
  total_triggered_count: number;
  fraud_precision_rate: number;
  created_at: string;
}

export interface RuleDryRunResult {
  is_triggered: boolean;
  evaluation_result: boolean;
  latency_microseconds: number;
  matched_variables: Record<string, any>;
  error_message?: string | null;
}

export interface RuleBacktestResult {
  total_evaluated: number;
  total_triggered: number;
  trigger_percentage: number;
  fraud_catch_rate: number;
  false_positive_rate: number;
  estimated_monthly_decline_volume: number;
}
