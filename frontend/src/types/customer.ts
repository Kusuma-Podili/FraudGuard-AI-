import { TransactionRecord } from "./transaction";
import { FraudAlert } from "./alert";
import { InvestigationCase } from "./case";

export interface CustomerProfile {
  id: string;
  customer_id: string;
  card_id: string;
  masked_card: string;
  full_name: string;
  email?: string;
  phone?: string;
  card_type: string;
  card_network: string;
  card_status: "ACTIVE" | "FROZEN" | "BLOCKED";
  risk_tier: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  avg_amount_30d: number;
  max_amount_single: number;
  typical_categories: string[];
  typical_locations: string[];
  known_devices: string[];
  total_transactions_count: number;
  total_fraud_alerts_count: number;
  total_cases_count: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CustomerDossier {
  profile: CustomerProfile;
  recent_transactions: TransactionRecord[];
  recent_alerts: FraudAlert[];
  recent_cases: InvestigationCase[];
  behavioral_baseline: {
    avg_amount_30d: number;
    max_amount_single: number;
    typical_categories: string[];
    typical_locations: string[];
    known_devices: string[];
    total_transactions: number;
    total_alerts: number;
    total_cases: number;
  };
}
