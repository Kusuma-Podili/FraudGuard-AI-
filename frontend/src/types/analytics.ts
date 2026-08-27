export interface DashboardKPIs {
  total_transactions_24h: number;
  total_volume_usd_24h: number;
  fraud_prevented_usd_24h: number;
  fraud_rate_percentage: number;
  active_threat_level: "NORMAL" | "ELEVATED" | "HIGH" | "SEVERE";
  open_cases_count: number;
  avg_inference_latency_ms: number;
  p99_inference_latency_ms: number;
  system_tps: number;
}

export interface HourlyTrendPoint {
  hour: string;
  total_count: number;
  fraud_count: number;
  volume_usd: number;
  blocked_volume_usd: number;
}

export interface MerchantRiskItem {
  merchant_id: string;
  name: string;
  category: string;
  risk_score: number;
  fraud_rate: number;
  total_volume: number;
  is_blacklisted: boolean;
}

export interface GeoRiskItem {
  country_code: string;
  country_name: string;
  risk_score: number;
  transaction_count: number;
  fraud_count: number;
}
