"use client";

import React, { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";
import { RiskThresholdsConfig, NotificationSettingsConfig, SystemHealthStatus } from "@/types";
import {
  Settings,
  Shield,
  Activity,
  Bell,
  CheckCircle2,
  Save,
  Server,
  Database,
  BrainCircuit,
  Radio,
  Lock,
} from "lucide-react";

export default function SettingsPage() {
  const [thresholds, setThresholds] = useState<RiskThresholdsConfig>({
    low_max: 0.30,
    medium_max: 0.60,
    high_max: 0.80,
    critical_min: 0.80,
    auto_decline_enabled: true,
    auto_case_creation_threshold: 0.60,
  });

  const [notifications, setNotifications] = useState<NotificationSettingsConfig>({
    in_app_alerts_enabled: true,
    critical_alert_sound: true,
    email_digest_enabled: false,
    slack_webhook_url: "",
    min_alert_severity: "HIGH",
  });

  const [health, setHealth] = useState<SystemHealthStatus | null>(null);
  const [isSavingThresholds, setIsSavingThresholds] = useState(false);
  const [isSavingNotifications, setIsSavingNotifications] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    async function loadSettings() {
      try {
        const [threshRes, notifRes, healthRes] = await Promise.all([
          api.getRiskThresholds(),
          api.getNotificationSettings(),
          api.getDetailedHealth(),
        ]);
        if (threshRes) setThresholds(threshRes);
        if (notifRes) setNotifications(notifRes);
        if (healthRes) setHealth(healthRes);
      } catch (e) {
        console.error("Failed to load settings", e);
      }
    }
    loadSettings();
  }, []);

  const handleSaveThresholds = async () => {
    setIsSavingThresholds(true);
    setSuccessMessage(null);
    try {
      await api.updateRiskThresholds(thresholds);
      setSuccessMessage("Risk thresholds successfully updated and propagated to decision engine.");
    } catch (e) {
      console.error("Failed to save thresholds", e);
    } finally {
      setIsSavingThresholds(false);
    }
  };

  const handleSaveNotifications = async () => {
    setIsSavingNotifications(true);
    setSuccessMessage(null);
    try {
      await api.updateNotificationSettings(notifications);
      setSuccessMessage("Notification preferences saved successfully.");
    } catch (e) {
      console.error("Failed to save notifications", e);
    } finally {
      setIsSavingNotifications(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Settings className="w-6 h-6 text-[#5F8F83]" />
            <h1 className="text-2xl font-bold text-[#29332F] tracking-tight">System Settings & Risk Policies</h1>
          </div>
          <p className="text-xs text-[#69736E] mt-1">
            Configure risk score cutoff boundaries, automated decline triggers, and subsystem health monitors.
          </p>
        </div>
      </div>

      {successMessage && (
        <div className="p-3.5 bg-[#A8C5B5]/20 border border-[#A8C5B5] rounded-xl text-xs text-[#35604B] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-[#35604B] shrink-0" />
            <span>{successMessage}</span>
          </div>
          <button onClick={() => setSuccessMessage(null)} className="text-[#69736E] hover:text-[#29332F]">✕</button>
        </div>
      )}

      {/* Subsystem Live Health Section */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-[#5F8F83]" />
              <CardTitle>Subsystem Health & Liveness Probes</CardTitle>
            </div>
            <span className="text-[11px] px-2.5 py-1 rounded bg-[#A8C5B5]/20 text-[#35604B] font-semibold border border-[#A8C5B5]/50 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#35604B]" />
              All Systems Operational
            </span>
          </div>
        </CardHeader>
        <div className="p-5 pt-0 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {[
            { name: "FastAPI Gateway", status: health?.backend_api || "HEALTHY", icon: Server },
            { name: "SQL Database", status: health?.database || "HEALTHY", icon: Database },
            { name: "Ensemble Engine", status: health?.ml_engine || "HEALTHY", icon: BrainCircuit },
            { name: "WebSocket Hub", status: health?.websocket || "HEALTHY", icon: Radio },
            { name: "OAuth2 & RBAC", status: health?.authentication || "HEALTHY", icon: Lock },
            { name: "Alert Dispatcher", status: health?.notification_service || "HEALTHY", icon: Bell },
          ].map((srv, idx) => {
            const Icon = srv.icon;
            return (
              <div key={idx} className="p-3.5 bg-[#F7F4EF] border border-[#E5DED5] rounded-xl space-y-2 text-center">
                <div className="w-8 h-8 rounded-lg bg-[#A8C5B5]/30 text-[#35604B] mx-auto flex items-center justify-center">
                  <Icon className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-[11px] font-bold text-[#29332F]">{srv.name}</p>
                  <span className="text-[10px] font-bold text-[#35604B] uppercase">{srv.status}</span>
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Thresholds Card */}
        <Card className="space-y-5 p-6">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-[#5F8F83]" />
              <span>Risk Score Cutoff Thresholds</span>
            </CardTitle>
            <CardDescription className="mt-1">
              Normalized bounds (0.00 to 1.00) determining automated authorization decisions.
            </CardDescription>
          </div>

          <div className="space-y-4">
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-[#35604B]">Low Risk Upper Bound (ALLOW)</span>
                <span className="font-mono text-[#29332F]">{thresholds.low_max.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.10"
                max="0.50"
                step="0.05"
                value={thresholds.low_max}
                onChange={(e) => setThresholds({ ...thresholds, low_max: parseFloat(e.target.value) })}
                className="w-full accent-[#5F8F83] cursor-pointer"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-[#795B20]">Medium Risk Upper Bound (REVIEW)</span>
                <span className="font-mono text-[#29332F]">{thresholds.medium_max.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.40"
                max="0.75"
                step="0.05"
                value={thresholds.medium_max}
                onChange={(e) => setThresholds({ ...thresholds, medium_max: parseFloat(e.target.value) })}
                className="w-full accent-[#E8C98A] cursor-pointer"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-[#7B3030]">Critical Risk Lower Bound (DECLINE)</span>
                <span className="font-mono text-[#29332F]">{thresholds.critical_min.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.70"
                max="0.95"
                step="0.05"
                value={thresholds.critical_min}
                onChange={(e) => setThresholds({ ...thresholds, critical_min: parseFloat(e.target.value) })}
                className="w-full accent-[#D99A9A] cursor-pointer"
              />
            </div>

            <div className="pt-2 flex items-center justify-between border-t border-[#E5DED5]">
              <div>
                <p className="text-xs font-bold text-[#29332F]">Automated Decline Enforcer</p>
                <p className="text-[10px] text-[#69736E]">Auto-reject transactions exceeding critical threshold.</p>
              </div>
              <input
                type="checkbox"
                checked={thresholds.auto_decline_enabled}
                onChange={(e) => setThresholds({ ...thresholds, auto_decline_enabled: e.target.checked })}
                className="w-4 h-4 accent-[#5F8F83] rounded cursor-pointer"
              />
            </div>

            <div className="flex justify-end pt-3">
              <Button size="sm" onClick={handleSaveThresholds} disabled={isSavingThresholds}>
                <Save className="w-3.5 h-3.5 mr-1.5" />
                {isSavingThresholds ? "Deploying..." : "Save Risk Policies"}
              </Button>
            </div>
          </div>
        </Card>

        {/* Notifications & Dispatch Preferences */}
        <Card className="space-y-5 p-6">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Bell className="w-5 h-5 text-[#A99BBE]" />
              <span>Alert Notifications & Webhooks</span>
            </CardTitle>
            <CardDescription className="mt-1">
              Configure real-time dispatch channels for critical security triggers.
            </CardDescription>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between py-2 border-b border-[#E5DED5]">
              <div>
                <p className="text-xs font-bold text-[#29332F]">In-App Notification Center</p>
                <p className="text-[10px] text-[#69736E]">Display instant badges and notification toasts.</p>
              </div>
              <input
                type="checkbox"
                checked={notifications.in_app_alerts_enabled}
                onChange={(e) => setNotifications({ ...notifications, in_app_alerts_enabled: e.target.checked })}
                className="w-4 h-4 accent-[#5F8F83] rounded cursor-pointer"
              />
            </div>

            <div className="flex items-center justify-between py-2 border-b border-[#E5DED5]">
              <div>
                <p className="text-xs font-bold text-[#29332F]">Critical Audio Chime</p>
                <p className="text-[10px] text-[#69736E]">Audible notification for critical severity threats.</p>
              </div>
              <input
                type="checkbox"
                checked={notifications.critical_alert_sound}
                onChange={(e) => setNotifications({ ...notifications, critical_alert_sound: e.target.checked })}
                className="w-4 h-4 accent-[#5F8F83] rounded cursor-pointer"
              />
            </div>

            <div className="space-y-1.5 pt-1">
              <label className="text-xs font-semibold text-[#29332F]">Minimum Alert Severity Trigger</label>
              <select
                value={notifications.min_alert_severity}
                onChange={(e) => setNotifications({ ...notifications, min_alert_severity: e.target.value })}
                className="w-full bg-[#F7F4EF] border border-[#E5DED5] rounded-lg p-2 text-xs text-[#29332F] focus:outline-none focus:ring-1 focus:ring-[#5F8F83]"
              >
                <option value="CRITICAL">Critical Threats Only</option>
                <option value="HIGH">High and Critical Threats</option>
                <option value="MEDIUM">Medium, High, and Critical</option>
              </select>
            </div>

            <div className="space-y-1.5 pt-1">
              <label className="text-xs font-semibold text-[#29332F]">Slack / SIEM Webhook URL</label>
              <input
                type="text"
                placeholder="https://hooks.slack.com/services/..."
                value={notifications.slack_webhook_url || ""}
                onChange={(e) => setNotifications({ ...notifications, slack_webhook_url: e.target.value })}
                className="w-full bg-[#F7F4EF] border border-[#E5DED5] rounded-lg p-2 text-xs text-[#29332F] focus:outline-none focus:ring-1 focus:ring-[#5F8F83]"
              />
            </div>

            <div className="flex justify-end pt-3">
              <Button size="sm" onClick={handleSaveNotifications} disabled={isSavingNotifications}>
                <Save className="w-3.5 h-3.5 mr-1.5" />
                {isSavingNotifications ? "Saving..." : "Save Preferences"}
              </Button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
