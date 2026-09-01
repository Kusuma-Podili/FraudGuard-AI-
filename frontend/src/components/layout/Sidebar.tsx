"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Radio,
  ShieldAlert,
  CreditCard,
  Scale,
  BrainCircuit,
  BarChart3,
  Flame,
  Settings,
  ShieldCheck,
  Users,
  FileText,
  History,
  Bell,
  UserCheck,
  User,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const { user, isAdmin, logout } = useAuth();

  const adminNav = [
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

  const analystNav = [
    { name: "Analyst Triage Queue", href: "/", icon: LayoutDashboard },
    { name: "Live Threat Radar", href: "/live-monitor", icon: Radio, badge: "LIVE" },
    { name: "Alert Center", href: "/alerts", icon: Bell, badge: "ALERT" },
    { name: "Investigation Cases", href: "/cases", icon: ShieldAlert },
    { name: "Transactions Query", href: "/transactions", icon: CreditCard },
    { name: "Customer & Card 360", href: "/customers", icon: UserCheck },
    { name: "Compliance Reports", href: "/reports", icon: FileText },
    { name: "Attack Sandbox", href: "/simulator", icon: Flame },
  ];

  const navItems = isAdmin ? adminNav : analystNav;

  return (
    <aside className="w-64 bg-[#0B1220] border-r border-gray-800/80 flex flex-col justify-between shrink-0 h-screen sticky top-0 z-40 select-none shadow-2xl">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center gap-3 px-6 border-b border-gray-800/80 bg-[#0B1220]">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/25 ring-1 ring-white/10">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-gray-100 tracking-wide">FRAUDGUARD AI</h1>
            <p className="text-[10px] text-blue-400 font-semibold tracking-wider uppercase">
              {isAdmin ? "Admin Console" : "Analyst Operations"}
            </p>
          </div>
        </div>

        {/* Navigation links */}
        <nav className="p-3.5 space-y-1 overflow-y-auto max-h-[calc(100vh-140px)]">
          <div className="px-3 py-1 text-[10px] font-bold text-gray-500 uppercase tracking-wider">
            {isAdmin ? "System Management" : "Investigation Workflows"}
          </div>
          {navItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-all group",
                  isActive
                    ? "bg-blue-600/15 text-blue-400 border border-blue-500/30 font-semibold shadow-sm"
                    : "text-gray-400 hover:text-gray-200 hover:bg-gray-900/60"
                )}
              >
                <div className="flex items-center gap-3">
                  <Icon className={cn("w-4 h-4 transition-colors shrink-0", isActive ? "text-blue-400" : "text-gray-500 group-hover:text-gray-300")} />
                  <span className="truncate">{item.name}</span>
                </div>
                {item.badge && (
                  <span
                    className={cn(
                      "px-1.5 py-0.5 rounded text-[9px] font-bold uppercase",
                      item.badge === "LIVE"
                        ? "bg-red-500 text-white animate-pulse"
                        : "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                    )}
                  >
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* User Session Footer */}
      <div className="p-3 border-t border-gray-800/80 m-3 rounded-xl bg-gray-950/60 border border-gray-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-7 h-7 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0">
              <User className="w-3.5 h-3.5" />
            </div>
            <div className="min-w-0">
              <p className="text-[11px] font-bold text-gray-200 truncate">{user?.full_name || "Demo User"}</p>
              <span className="text-[9px] px-1.5 py-0.2 rounded bg-blue-950 text-blue-400 font-semibold border border-blue-800/40">
                {user?.role || "ADMIN"}
              </span>
            </div>
          </div>
          <button
            onClick={logout}
            className="text-[10px] text-gray-400 hover:text-red-400 transition-colors p-1"
            title="Sign out"
          >
            Logout
          </button>
        </div>
      </div>
    </aside>
  );
};
