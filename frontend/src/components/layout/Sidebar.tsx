"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Radio,
  ShieldAlert,
  Scale,
  BrainCircuit,
  BarChart3,
  Flame,
  Settings,
  ShieldCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigationItems = [
  { name: "Executive Overview", href: "/", icon: LayoutDashboard },
  { name: "Live Threat Radar", href: "/live-monitor", icon: Radio, badge: "LIVE" },
  { name: "Investigation Cases", href: "/cases", icon: ShieldAlert },
  { name: "Visual Rule Studio", href: "/rules", icon: Scale },
  { name: "MLOps & Models", href: "/models", icon: BrainCircuit },
  { name: "Deep Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Attack Sandbox", href: "/simulator", icon: Flame },
  { name: "System Settings", href: "/settings", icon: Settings },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-gray-950/95 border-r border-gray-800 flex flex-col justify-between shrink-0 h-screen sticky top-0 z-40">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center gap-3 px-6 border-b border-gray-800">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-gray-100 tracking-wide">FRAUDGUARD AI</h1>
            <p className="text-[10px] text-blue-400 font-semibold tracking-wider uppercase">Enterprise Defense</p>
          </div>
        </div>

        {/* Navigation links */}
        <nav className="p-4 space-y-1">
          {navigationItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all group",
                  isActive
                    ? "bg-blue-600/10 text-blue-400 border border-blue-500/20 font-semibold"
                    : "text-gray-400 hover:text-gray-200 hover:bg-gray-900/60"
                )}
              >
                <div className="flex items-center gap-3">
                  <Icon className={cn("w-4 h-4 transition-colors", isActive ? "text-blue-400" : "text-gray-500 group-hover:text-gray-300")} />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-red-500 text-white animate-pulse">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* System Status Footer */}
      <div className="p-4 border-t border-gray-800/80 m-4 rounded-xl bg-gray-900/40 border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
            <span className="text-[11px] font-semibold text-gray-300">Gateway Active</span>
          </div>
          <span className="text-[10px] text-gray-500 font-mono">v1.0.0</span>
        </div>
        <p className="text-[10px] text-gray-500 mt-1">Sub-20ms Decision Engine</p>
      </div>
    </aside>
  );
};
