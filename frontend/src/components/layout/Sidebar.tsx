"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import {
  ShieldAlert,
  CreditCard,
  Bell,
  FileText,
  Users,
  Settings,
  History,
  LayoutDashboard,
  BrainCircuit,
  BarChart3,
  UserCheck,
  Radio,
  LogOut,
  ChevronRight,
  ShieldCheck,
} from "lucide-react";

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const { user, isAdmin, isAnalyst, logout, role, setRole } = useAuth();

  const adminNavItems = [
    { name: "Executive Overview", href: "/", icon: LayoutDashboard },
    { name: "All Transactions", href: "/transactions", icon: CreditCard },
    { name: "Fraud Analytics", href: "/analytics", icon: BarChart3 },
    { name: "Fraud Cases", href: "/cases", icon: ShieldAlert },
    { name: "Alert Center", href: "/alerts", icon: Bell, badge: "ACTIVE" },
    { name: "ML Models & Drift", href: "/models", icon: BrainCircuit },
    { name: "Reports & Export", href: "/reports", icon: FileText },
    { name: "User Management", href: "/users", icon: Users },
    { name: "System Settings", href: "/settings", icon: Settings },
    { name: "Audit Trail Logs", href: "/audit-logs", icon: History },
  ];

  const analystNavItems = [
    { name: "Analyst Triage Queue", href: "/", icon: LayoutDashboard },
    { name: "Live Threat Radar", href: "/live-monitor", icon: Radio, badge: "LIVE" },
    { name: "Alert Center", href: "/alerts", icon: Bell, badge: "ALERT" },
    { name: "Investigation Cases", href: "/cases", icon: ShieldAlert },
    { name: "Transactions Query", href: "/transactions", icon: CreditCard },
    { name: "Customer & Card 360", href: "/customers", icon: UserCheck },
    { name: "Compliance Reports", href: "/reports", icon: FileText },
  ];

  const navItems = isAdmin ? adminNavItems : analystNavItems;

  return (
    <aside className="w-64 bg-white border-r border-[#E5E7EB] flex flex-col justify-between shrink-0 h-screen sticky top-0 z-40 shadow-sm">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center gap-3 px-5 border-b border-[#E5E7EB] bg-white">
          <div className="w-8 h-8 rounded-lg bg-[#FFEDD5] text-[#EA580C] flex items-center justify-center font-bold text-sm border border-[#FDBA74]">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-[#111827] tracking-tight">FraudGuard AI</h1>
            <p className="text-[10px] text-[#6B7280] font-semibold tracking-wider uppercase">
              {isAdmin ? "Admin Console" : "Analyst Operations"}
            </p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-3 space-y-1 overflow-y-auto max-h-[calc(100vh-140px)]">
          <div className="px-3 py-1 text-[10px] font-bold text-[#9CA3AF] uppercase tracking-wider">
            {isAdmin ? "System Management" : "Investigation Workflows"}
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? "bg-[#FFF7ED] text-[#9A3412] font-semibold border-l-2 border-[#FB923C]"
                    : "text-[#374151] hover:bg-gray-100 hover:text-[#111827]"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span
                    className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                      item.badge === "LIVE"
                        ? "bg-[#FFEDD5] text-[#9A3412]"
                        : "bg-gray-100 text-gray-700 border border-gray-300"
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* User Profile & Demo Switcher Footer */}
      <div className="p-3 border-t border-[#E5E7EB] m-3 rounded-lg bg-[#F9FAFB] border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-7 h-7 rounded-md bg-[#FFEDD5] flex items-center justify-center text-[#EA580C] shrink-0 font-bold text-xs">
              {user?.full_name?.charAt(0) || "U"}
            </div>
            <div className="min-w-0">
              <p className="text-[11px] font-bold text-[#111827] truncate">
                {user?.full_name || "Enterprise User"}
              </p>
              <span className="text-[9px] px-1.5 py-0.2 rounded bg-gray-200 text-gray-700 font-semibold">
                {role}
              </span>
            </div>
          </div>

          <button
            onClick={() => setRole(isAdmin ? "FRAUD_ANALYST" : "ADMIN")}
            className="text-[10px] text-[#EA580C] hover:text-[#9A3412] font-semibold px-2 py-1 bg-white hover:bg-[#FFF7ED] rounded border border-[#E5E7EB] transition-colors"
            title="Toggle Demo Role"
          >
            Switch
          </button>
        </div>
      </div>
    </aside>
  );
};
