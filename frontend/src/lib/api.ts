import axios, { AxiosInstance } from "axios";
import { API_BASE_URL } from "./constants";
import {
  APIResponse,
  PaginatedResponse,
  TransactionRecord,
  InvestigationCase,
  FraudRule,
  ModelRegistryRecord,
  ExplainabilityData,
  DashboardKPIs,
  HourlyTrendPoint,
  MerchantRiskItem,
  GeoRiskItem,
  RuleDryRunResult,
  RuleBacktestResult,
} from "../types";

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

// Interceptor to attach JWT token
apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("fraudguard_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export const api = {
  // Auth
  async login(email: string, password: string) {
    const res = await apiClient.post<APIResponse<{ access_token: string; user_id: string; role: string; full_name: string }>>("/auth/login/json", {
      email,
      password,
    });
    return res.data.data;
  },

  async getMe() {
    const res = await apiClient.get<APIResponse<any>>("/auth/me");
    return res.data.data;
  },

  // Transactions
  async scoreTransaction(payload: Record<string, any>) {
    const res = await apiClient.post<APIResponse<any>>("/transactions/score", payload);
    return res.data.data;
  },

  async listTransactions(params: { page?: number; page_size?: number; min_score?: number; action?: string; card_id?: string } = {}) {
    const res = await apiClient.get<APIResponse<PaginatedResponse<TransactionRecord>>>("/transactions", { params });
    return res.data.data;
  },

  // Cases
  async listCases(params: { page?: number; page_size?: number; status?: string; severity?: string; assigned_to_me?: boolean } = {}) {
    const res = await apiClient.get<APIResponse<PaginatedResponse<InvestigationCase>>>("/cases", { params });
    return res.data.data;
  },

  async getCaseById(caseId: string) {
    const res = await apiClient.get<APIResponse<InvestigationCase>>(`/cases/${caseId}`);
    return res.data.data;
  },

  async updateCaseStatus(caseId: string, status: string, reason?: string, note?: string) {
    const res = await apiClient.patch<APIResponse<InvestigationCase>>(`/cases/${caseId}/status`, {
      status,
      resolution_reason: reason,
      note,
    });
    return res.data.data;
  },

  async assignCase(caseId: string, analystId: string, analystName: string) {
    const res = await apiClient.post<APIResponse<InvestigationCase>>(`/cases/${caseId}/assign`, {
      analyst_id: analystId,
      analyst_name: analystName,
    });
    return res.data.data;
  },

  async addCaseNote(caseId: string, content: string) {
    const res = await apiClient.post<APIResponse<any>>(`/cases/${caseId}/notes`, { content });
    return res.data.data;
  },

  // Rules
  async listRules(category?: string) {
    const res = await apiClient.get<APIResponse<FraudRule[]>>("/rules", { params: { category } });
    return res.data.data;
  },

  async createRule(payload: Partial<FraudRule>) {
    const res = await apiClient.post<APIResponse<FraudRule>>("/rules", payload);
    return res.data.data;
  },

  async dryRunRule(condition: string, sampleTx: Record<string, any>) {
    const res = await apiClient.post<APIResponse<RuleDryRunResult>>("/rules/dry-run", {
      condition_expression: condition,
      sample_transaction: sampleTx,
    });
    return res.data.data;
  },

  async backtestRule(condition: string, samples: number = 500) {
    const res = await apiClient.post<APIResponse<RuleBacktestResult>>("/rules/backtest", {
      condition_expression: condition,
      historical_samples_count: samples,
    });
    return res.data.data;
  },

  // Models
  async listModels() {
    const res = await apiClient.get<APIResponse<ModelRegistryRecord[]>>("/models");
    return res.data.data;
  },

  async promoteModel(modelId: string) {
    const res = await apiClient.post<APIResponse<ModelRegistryRecord>>(`/models/${modelId}/promote`);
    return res.data.data;
  },

  async getLiveModelMetrics() {
    const res = await apiClient.get<APIResponse<any>>("/models/metrics/live");
    return res.data.data;
  },

  // Explainability
  async getExplanation(txId?: string, payload?: Record<string, any>) {
    const res = await apiClient.post<APIResponse<ExplainabilityData>>("/explain", {
      transaction_id: txId,
      transaction_payload: payload,
    });
    return res.data.data;
  },

  // Simulation
  async controlSimulator(action: string, tps?: number, attackType?: string, duration?: number) {
    const res = await apiClient.post<APIResponse<any>>("/simulation/control", {
      action,
      target_tps: tps,
      attack_type: attackType,
      duration_seconds: duration,
    });
    return res.data.data;
  },

  async getSimulatorStatus() {
    const res = await apiClient.get<APIResponse<any>>("/simulation/status");
    return res.data.data;
  },

  // Analytics
  async getDashboardKPIs() {
    const res = await apiClient.get<APIResponse<DashboardKPIs>>("/analytics/summary");
    return res.data.data;
  },

  async getHourlyTrends() {
    const res = await apiClient.get<APIResponse<HourlyTrendPoint[]>>("/analytics/hourly-trends");
    return res.data.data;
  },

  async getTopMerchants() {
    const res = await apiClient.get<APIResponse<MerchantRiskItem[]>>("/analytics/merchants");
    return res.data.data;
  },

  async getGeoRiskHeatmap() {
    const res = await apiClient.get<APIResponse<GeoRiskItem[]>>("/analytics/geo-heatmap");
    return res.data.data;
  },
};
