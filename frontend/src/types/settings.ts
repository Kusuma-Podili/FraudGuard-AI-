export interface RiskThresholdsConfig {
  low_max: number;
  medium_max: number;
  high_max: number;
  critical_min: number;
  auto_decline_enabled: boolean;
  auto_case_creation_threshold: number;
}

export interface NotificationSettingsConfig {
  in_app_alerts_enabled: boolean;
  critical_alert_sound: boolean;
  email_digest_enabled: boolean;
  slack_webhook_url?: string;
  min_alert_severity: string;
}

export interface SystemHealthStatus {
  backend_api: string;
  database: string;
  ml_engine: string;
  websocket: string;
  authentication: string;
  notification_service: string;
  p99_latency_ms: number;
  uptime_seconds: number;
  active_connections: number;
}
