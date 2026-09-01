import axios, { AxiosInstance } from "axios";
import { API_BASE_URL } from "./constants";
import {
  APIResponse,
  PaginatedResponse,
  TransactionRecord,
  InvestigationCase,
  FraudAlert,
  CustomerProfile,
  CustomerDossier,
  FraudRule,
  ModelRegistryRecord,
  ExplainabilityData,
  DashboardKPIs,
  HourlyTrendPoint,
  MerchantRiskItem,
  GeoRiskItem,
  RuleDryRunResult,
  RuleBacktestResult,
  ReportGenerateRequest,
  ReportSummaryDTO,
  RiskThresholdsConfig,
  NotificationSettingsConfig,
  SystemHealthStatus,
  User,
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
    const res = await apiClient.get<APIResponse<User>>("/auth/me");
    return res.data.data;
  },

  // Transactions
  async scoreTransaction(payload: Record<string, any>) {
    const res = await apiClient.post<APIResponse<any>>("/transactions/score", payload);
    return res.data.data;
  },

  async listTransactions(params: {
    page?: number;
    page_size?: number;
    search?: string;
    risk_level?: string;
    decision?: string;
    merchant?: string;
    category?: string;
    channel?: string;
    min_amount?: number;
    max_amount?: number;
    min_score?: number;
    card_id?: string;
  } = {}) {
    const res = await apiClient.get<APIResponse<PaginatedResponse<TransactionRecord>>>("/transactions", { params });
    return res.data.data;
  },

  async getTransactionDetail(txId: string) {
    const res = await apiClient.get<APIResponse<{ transaction: TransactionRecord; masked_card: string; customer_baseline: any }>>(`/transactions/${txId}`);
    return res.data.data;
  },

  // Alerts
  async listAlerts(params: {
    page?: number;
    page_size?: number;
    status?: string;
    severity?: string;
    search?: string;
  } = {}) {
    const res = await apiClient.get<APIResponse<PaginatedResponse<FraudAlert>>>("/alerts", { params });
    return res.data.data;
  },

  async getAlertById(alertId: string) {
    const res = await apiClient.get<APIResponse<FraudAlert>>(`/alerts/${alertId}`);
    return res.data.data;
  },

  async updateAlertStatus(alertId: string, status: string, notes?: string) {
    const res = await apiClient.patch<APIResponse<FraudAlert>>(`/alerts/${alertId}/status`, {
      status,
      resolution_notes: notes,
    });
    return res.data.data;
  },

  async assignAlert(alertId: string, analystId: string, analystName: string) {
    const res = await apiClient.post<APIResponse<FraudAlert>>(`/alerts/${alertId}/assign`, {
      analyst_id: analystId,
      analyst_name: analystName,
    });
    return res.data.data;
  },

  async convertAlertToCase(alertId: string) {
    const res = await apiClient.post<APIResponse<InvestigationCase>>(`/alerts/${alertId}/convert-case`);
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

  // Customers
  async listCustomers(params: { page?: number; page_size?: number; risk_tier?: string; search?: string } = {}) {
    const res = await apiClient.get<APIResponse<PaginatedResponse<CustomerProfile>>>("/customers", { params });
    return res.data.data;
  },

  async getCustomerDossier(identifier: string) {
    const res = await apiClient.get<APIResponse<CustomerDossier>>(`/customers/${identifier}/dossier`);
    return res.data.data;
  },

  // Reports
  async generateReport(req: ReportGenerateRequest) {
    const res = await apiClient.post<APIResponse<ReportSummaryDTO>>("/reports/generate", req);
    return res.data.data;
  },

  getReportCsvDownloadUrl(type: string) {
    return `${API_BASE_URL}/reports/export/csv?type=${type}`;
  },

  // Users (Admin)
  async listUsers() {
    const res = await apiClient.get<APIResponse<User[]>>("/users");
    return res.data.data;
  },

  async createUser(payload: { email: string; password: string; full_name: string; role: string; department?: string }) {
    const res = await apiClient.post<APIResponse<User>>("/users", payload);
    return res.data.data;
  },

  async updateUser(userId: string, payload: Partial<User>) {
    const res = await apiClient.patch<APIResponse<User>>(`/users/${userId}`, payload);
    return res.data.data;
  },

  async resetUserPassword(userId: string, newPassword: string) {
    const res = await apiClient.post<APIResponse<any>>(`/users/${userId}/reset-password`, { new_password: newPassword });
    return res.data.data;
  },

  // Settings & System Health (Admin)
  async getRiskThresholds() {
    const res = await apiClient.get<APIResponse<RiskThresholdsConfig>>("/settings/risk-thresholds");
    return res.data.data;
  },

  async updateRiskThresholds(payload: RiskThresholdsConfig) {
    const res = await apiClient.post<APIResponse<RiskThresholdsConfig>>("/settings/risk-thresholds", payload);
    return res.data.data;
  },

  async getNotificationSettings() {
    const res = await apiClient.get<APIResponse<NotificationSettingsConfig>>("/settings/notifications");
    return res.data.data;
  },

  async updateNotificationSettings(payload: NotificationSettingsConfig) {
    const res = await apiClient.post<APIResponse<NotificationSettingsConfig>>("/settings/notifications", payload);
    return res.data.data;
  },

  async getDetailedHealth() {
    const res = await apiClient.get<APIResponse<SystemHealthStatus>>("/settings/health-detailed");
    return res.data.data;
  },

  // Audit Logs (Admin)
  async listAuditLogs(params: { page?: number; page_size?: number; action_type?: string } = {}) {
    const res = await apiClient.get<APIResponse<PaginatedResponse<any>>>("/audit", { params });
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

  // Explainability (XAI)
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
  async getDashboardKPIs(dateRange: string = "30d") {
    const res = await apiClient.get<APIResponse<any>>("/analytics/summary", { params: { date_range: dateRange } });
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
