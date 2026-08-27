export type CaseStatus =
  | "OPEN"
  | "IN_REVIEW"
  | "ESCALATED"
  | "CONFIRMED_FRAUD"
  | "FALSE_POSITIVE"
  | "CHARGEBACK_FILED"
  | "RESOLVED";

export type CaseSeverity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface CaseNote {
  id: string;
  case_id: string;
  author_name: string;
  content: string;
  is_internal_only: string;
  created_at: string;
}

export interface InvestigationCase {
  id: string;
  case_number: string;
  transaction_id: string;
  card_id: string;
  cardholder_id: string;
  amount: number;
  risk_score: number;
  severity: CaseSeverity;
  status: CaseStatus;
  assigned_analyst_name?: string;
  summary?: string;
  resolution_reason?: string;
  evidence_payload: Record<string, any>;
  sla_due_at?: string;
  created_at: string;
  notes: CaseNote[];
}
