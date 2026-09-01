export type AlertSeverity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type AlertStatus =
  | "NEW"
  | "ASSIGNED"
  | "UNDER_REVIEW"
  | "ESCALATED"
  | "RESOLVED"
  | "FALSE_POSITIVE"
  | "CASE_CREATED";

export interface FraudAlert {
  id: string;
  alert_id: string;
  transaction_id: string;
  card_id: string;
  cardholder_id?: string;
  severity: AlertSeverity;
  status: AlertStatus;
  risk_score: float;
  reason: string;
  triggered_rules: string[];
  amount: number;
  merchant_name?: string;
  location?: string;
  assigned_to_user_id?: string;
  assigned_analyst_name?: string;
  resolution_notes?: string;
  created_at: string;
  updated_at?: string;
}

type float = number;
