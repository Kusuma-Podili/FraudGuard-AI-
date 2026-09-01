"use client";

import React, { useState } from "react";
import { Search, Bell, Activity, UserCheck, ShieldCheck, LogOut, ArrowLeftRight } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import Link from "next/link";

export const Header: React.FC = () => {
  const { user, login, logout, isAdmin } = useAuth();
  const [switching, setSwitching] = useState(false);

  const handleRoleToggle = async () => {
    setSwitching(true);
    try {
      if (isAdmin) {
        // Switch to Analyst
        await login("analyst@fraudguard.ai", "Analyst@2026");
      } else {
        // Switch to Admin
        await login("admin@fraudguard.ai", "Admin@2026");
      }
    } catch (e) {
      console.error("Role switch failed", e);
    } finally {
      setSwitching(false);
    }
  };

  return (
    <header className="h-16 bg-[#0B1220]/90 border-b border-gray-800/80 flex items-center justify-between px-8 sticky top-0 z-30 backdrop-blur-md">
      {/* Search Input */}
      <div className="w-96 relative">
        <Search className="w-4 h-4 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          placeholder="Search card (e.g. 4829), transaction ID, merchant, case..."
          className="w-full bg-gray-900/90 border border-gray-800 rounded-lg pl-9 pr-4 py-1.5 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all"
        />
      </div>

      {/* Action Tray & User Status */}
      <div className="flex items-center gap-4">
        {/* Quick Role Switcher Button */}
        <button
          onClick={handleRoleToggle}
          disabled={switching}
          className="flex items-center gap-1.5 px-2.5 py-1.5 bg-blue-950/60 border border-blue-500/30 hover:border-blue-500/60 rounded-lg text-[11px] font-semibold text-blue-300 transition-all hover:bg-blue-900/40"
          title="Toggle between Admin and Fraud Analyst demo view"
        >
          <ArrowLeftRight className="w-3 h-3 text-blue-400" />
          <span>{switching ? "Switching..." : `Switch to ${isAdmin ? "Analyst" : "Admin"}`}</span>
        </button>

        {/* Latency Pill */}
        <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-900/90 border border-gray-800 rounded-lg">
          <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          <span className="text-xs text-gray-400 font-mono">
            p99: <strong className="text-emerald-400 font-semibold">14.2ms</strong>
          </span>
        </div>

        {/* Live Threat Status */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 bg-emerald-950/40 border border-emerald-500/30 rounded-lg">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-xs text-emerald-300 font-semibold">Defense Gateway Active</span>
        </div>

        {/* Notifications */}
        <Link
          href="/alerts"
          className="p-2 bg-gray-900/90 border border-gray-800 rounded-lg text-gray-400 hover:text-gray-200 transition-colors relative"
          title="View Alerts"
        >
          <Bell className="w-4 h-4" />
          <span className="w-2 h-2 rounded-full bg-red-500 absolute top-1.5 right-1.5 animate-pulse" />
        </Link>

        {/* User Pill */}
        <div className="flex items-center gap-3 pl-2 border-l border-gray-800">
          <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
            <UserCheck className="w-4 h-4" />
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-200 truncate max-w-[140px]">
              {user?.full_name || "Alexander Wright (CRO)"}
            </p>
            <p className="text-[10px] text-blue-400 font-semibold">{user?.role || "ADMIN"}</p>
          </div>
        </div>
      </div>
    </header>
  );
};
