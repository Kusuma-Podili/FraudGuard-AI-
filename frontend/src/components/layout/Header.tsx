"use client";

import React, { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/navigation";
import {
  Search,
  Bell,
  Code,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";

export const Header: React.FC = () => {
  const { user, isAdmin, setRole } = useAuth();
  const router = useRouter();
  const [search, setSearch] = useState("");

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (search.trim()) {
      router.push(`/transactions?search=${encodeURIComponent(search)}`);
    }
  };

  return (
    <header className="h-16 bg-white/95 border-b border-[#E5E7EB] flex items-center justify-between px-8 sticky top-0 z-30 backdrop-blur-sm shadow-sm">
      {/* Global Quick Search */}
      <form onSubmit={handleSearch} className="w-96 relative">
        <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search card (e.g. 4829), Tx ID, merchant, case..."
          className="w-full bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg pl-9 pr-4 py-1.5 text-xs text-[#111827] placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-[#FB923C] focus:border-[#FB923C]"
        />
      </form>

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* Latency Pill */}
        <div className="flex items-center gap-2 px-3 py-1.5 bg-white border border-[#E5E7EB] rounded-lg text-xs">
          <span className="w-2 h-2 rounded-full bg-[#FB923C]"></span>
          <span className="text-gray-500 font-mono">
            P99 SLA: <strong className="text-gray-900">14.2ms</strong>
          </span>
        </div>

        {/* Alerts Bell */}
        <Link href="/alerts">
          <button className="p-2 bg-white border border-[#E5E7EB] rounded-lg text-gray-500 hover:text-gray-900 transition-colors relative">
            <Bell className="w-4 h-4" />
            <span className="w-2 h-2 rounded-full bg-[#FB923C] absolute top-1.5 right-1.5" />
          </button>
        </Link>

        {/* API Docs link */}
        <a
          href="http://127.0.0.1:9000/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="px-3.5 py-1.5 rounded-lg bg-[#FB923C] hover:bg-[#F97316] text-xs font-semibold text-white shadow-sm flex items-center gap-1.5 transition-all"
        >
          <Code className="w-3.5 h-3.5" />
          <span>API Docs</span>
        </a>
      </div>
    </header>
  );
};
