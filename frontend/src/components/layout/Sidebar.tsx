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
    <aside className="w-64 bg-[#DCE7E1] border-r border-[#CCD9D2] flex flex-col justify-between shrink-0 h-screen sticky top-0 z-40 select-none shadow-sm">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center gap-3 px-5 border-b border-[#CCD9D2] bg-[#DCE7E1]">
          <div className="w-9 h-9 rounded-xl bg-[#5F8F83] flex items-center justify-center shadow-sm">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-[#26332F] tracking-tight">FraudGuard AI</h1>
            <p className="text-[10px] text-[#4F7D72] font-semibold tracking-wider uppercase">
              {isAdmin ? "Admin Console" : "Analyst Operations"}
            </p>
          </div>
        </div>

        {/* Navigation links */}
        <nav className="p-3 space-y-1 overflow-y-auto max-h-[calc(100vh-140px)]">
          <div className="px-3 py-1 text-[10px] font-bold text-[#69736E] uppercase tracking-wider">
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
                    ? "bg-[#C7D9D0] text-[#17231F] font-semibold border-l-2 border-[#5F8F83]"
                    : "text-[#26332F] hover:bg-[#C7D9D0]/60"
                )}
              >
                <div className="flex items-center gap-3">
                  <Icon className={cn("w-4 h-4 transition-colors shrink-0", isActive ? "text-[#5F8F83]" : "text-[#69736E] group-hover:text-[#26332F]")} />
                  <span className="truncate">{item.name}</span>
                </div>
                {item.badge && (
                  <span
                    className={cn(
                      "px-1.5 py-0.5 rounded text-[9px] font-bold uppercase",
                      item.badge === "LIVE"
                        ? "bg-[#D99A9A] text-[#7B3030]"
                        : "bg-[#C7D9D0] text-[#17231F] border border-[#B5CCC1]"
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
      <div className="p-3 border-t border-[#CCD9D2] m-3 rounded-xl bg-[#E6EFEA] border border-[#CCD9D2]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-7 h-7 rounded-lg bg-[#5F8F83]/20 flex items-center justify-center text-[#5F8F83] shrink-0 font-bold text-xs">
              <User className="w-3.5 h-3.5" />
            </div>
            <div className="min-w-0">
              <p className="text-[11px] font-bold text-[#26332F] truncate">
                {user?.full_name || (isAdmin ? "Alexander Wright" : "Sarah Chen")}
              </p>
              <span className="text-[9px] px-1.5 py-0.2 rounded bg-[#C7D9D0] text-[#17231F] font-semibold">
                {user?.role || (isAdmin ? "ADMIN" : "ANALYST")}
              </span>
            </div>
          </div>
          <button
            onClick={logout}
            className="text-[10px] text-[#4F7D72] hover:text-[#26332F] font-semibold px-2 py-1 bg-[#DCE7E1] hover:bg-[#C7D9D0] rounded border border-[#CCD9D2] transition-colors"
            title="Sign Out"
          >
            Logout
          </button>
        </div>
      </div>
    </aside>
  );
};
