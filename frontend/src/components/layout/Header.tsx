"use client";

import React, { useState } from "react";
import { Search, Bell, Activity, UserCheck, ShieldCheck, ArrowLeftRight } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import Link from "next/link";

export const Header: React.FC = () => {
  const { user, login, logout, isAdmin } = useAuth();
  const [switching, setSwitching] = useState(false);

  const handleRoleToggle = async () => {
    setSwitching(true);
    try {
      if (isAdmin) {
        await login("analyst@fraudguard.ai", "Analyst@2026");
      } else {
        await login("admin@fraudguard.ai", "Admin@2026");
      }
    } catch (e) {
      console.error("Role switch failed", e);
    } finally {
      setSwitching(false);
    }
  };

  return (
    <header className="h-16 bg-[#FFFDFC]/90 border-b border-[#E5DED5] flex items-center justify-between px-8 sticky top-0 z-30 backdrop-blur-md">
      {/* Search Input */}
      <div className="w-96 relative">
        <Search className="w-4 h-4 text-[#929A95] absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          placeholder="Search card (e.g. 4829), transaction ID, merchant, case..."
          className="w-full bg-[#F7F4EF] border border-[#E5DED5] rounded-lg pl-9 pr-4 py-1.5 text-xs text-[#29332F] placeholder-[#929A95] focus:outline-none focus:ring-1 focus:ring-[#5F8F83] focus:border-[#5F8F83] transition-all"
        />
      </div>

      {/* Action Tray & User Status */}
      <div className="flex items-center gap-4">
        {/* Quick Role Switcher Button */}
        <button
          onClick={handleRoleToggle}
          disabled={switching}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-[#DCE7E1] hover:bg-[#C7D9D0] border border-[#CCD9D2] rounded-lg text-xs font-semibold text-[#26332F] transition-all"
          title="Toggle between Admin and Fraud Analyst demo view"
        >
          <ArrowLeftRight className="w-3.5 h-3.5 text-[#5F8F83]" />
          <span>{switching ? "Switching..." : `Switch to ${isAdmin ? "Analyst" : "Admin"}`}</span>
        </button>

        {/* Latency Pill */}
        <div className="flex items-center gap-2 px-3 py-1.5 bg-[#FFFDFC] border border-[#E5DED5] rounded-lg">
          <Activity className="w-3.5 h-3.5 text-[#35604B]" />
          <span className="text-xs text-[#69736E] font-mono">
            p99: <strong className="text-[#35604B] font-semibold">14.2ms</strong>
          </span>
        </div>

        {/* Live Threat Status */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 bg-[#A8C5B5]/20 border border-[#A8C5B5]/50 rounded-lg">
          <span className="w-2 h-2 rounded-full bg-[#35604B]" />
          <span className="text-xs text-[#35604B] font-semibold">Gateway Active</span>
        </div>

        {/* Notifications */}
        <Link
          href="/alerts"
          className="p-2 bg-[#FFFDFC] border border-[#E5DED5] rounded-lg text-[#69736E] hover:text-[#29332F] transition-colors relative"
          title="View Alerts"
        >
          <Bell className="w-4 h-4" />
          <span className="w-2 h-2 rounded-full bg-[#D99A9A] absolute top-1.5 right-1.5" />
        </Link>

        {/* User Pill */}
        <div className="flex items-center gap-3 pl-2 border-l border-[#E5DED5]">
          <div className="w-8 h-8 rounded-lg bg-[#5F8F83]/15 flex items-center justify-center text-[#5F8F83] font-bold">
            <UserCheck className="w-4 h-4" />
          </div>
          <div>
            <p className="text-xs font-bold text-[#29332F] truncate max-w-[140px]">
              {user?.full_name || (isAdmin ? "Alexander Wright" : "Sarah Chen")}
            </p>
            <p className="text-[10px] text-[#4F7D72] font-semibold">{user?.role || (isAdmin ? "ADMIN" : "FRAUD_ANALYST")}</p>
          </div>
        </div>
      </div>
    </header>
  );
};
