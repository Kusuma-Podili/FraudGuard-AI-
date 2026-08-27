export interface ModelRegistryRecord {
  id: string;
  model_id: string;
  name: string;
  version: string;
  algorithm_type: string;
  status: "CHAMPION" | "CHALLENGER" | "CANDIDATE" | "RETIRED";
  traffic_percentage: number;
  roc_auc: number;
  pr_auc: number;
  f1_score: number;
  p99_latency_ms: number;
  description?: string;
  created_at: string;
}

export interface ShapWaterfallItem {
  feature: string;
  value: any;
  shap_value: number;
  direction: "INCREASES_RISK" | "REDUCES_RISK" | "NEUTRAL";
  impact_pct: number;
}

export interface CounterfactualItem {
  feature_name: string;
  original_value: any;
  recommended_value: any;
  change_description: string;
  is_actionable: boolean;
}

export interface ExplainabilityData {
  transaction_id: string;
  risk_score: number;
  base_value: number;
  decision_action: string;
  top_risk_factors: string[];
  top_protective_factors: string[];
  waterfall: ShapWaterfallItem[];
  counterfactuals: CounterfactualItem[];
  graph_syndicate_detected: boolean;
  graph_ring_telemetry: Record<string, any>;
}
