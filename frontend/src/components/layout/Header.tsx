"use client";

import React from "react";
import { Search, Bell, Activity, ShieldCheck, UserCheck } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

export const Header: React.FC = () => {
  const { user } = useAuth();

  return (
    <header className="h-16 bg-gray-950/80 border-b border-gray-800 flex items-center justify-between px-8 sticky top-0 z-30 backdrop-blur-md">
      {/* Search Input */}
      <div className="w-80 relative">
        <Search className="w-4 h-4 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          placeholder="Search card ID, transaction hash, merchant..."
          className="w-full bg-gray-900 border border-gray-800 rounded-lg pl-9 pr-4 py-1.5 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      {/* Action Tray & User Status */}
      <div className="flex items-center gap-4">
        {/* Latency Pill */}
        <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-900 border border-gray-800 rounded-lg">
          <Activity className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-xs text-gray-400 font-mono">p99: <strong className="text-emerald-400 font-semibold">14.2ms</strong></span>
        </div>

        {/* Notifications */}
        <button className="p-2 bg-gray-900 border border-gray-800 rounded-lg text-gray-400 hover:text-gray-200 transition-colors relative">
          <Bell className="w-4 h-4" />
          <span className="w-2 h-2 rounded-full bg-blue-500 absolute top-1.5 right-1.5"></span>
        </button>

        {/* User Pill */}
        <div className="flex items-center gap-3 pl-2 border-l border-gray-800">
          <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
            <UserCheck className="w-4 h-4" />
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-200">{user?.full_name || "Lead Fraud Analyst"}</p>
            <p className="text-[10px] text-gray-500">{user?.role || "FRAUD_ANALYST"}</p>
          </div>
        </div>
      </div>
    </header>
  );
};
