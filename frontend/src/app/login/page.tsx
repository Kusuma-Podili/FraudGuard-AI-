"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { ShieldCheck, Lock, Mail, ArrowRight, UserCheck, AlertCircle } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("admin@fraudguard.ai");
  const [password, setPassword] = useState("Admin@2026");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      await login(email, password);
      router.push("/");
    } catch (err: any) {
      setError(err?.response?.data?.message || "Invalid credentials or unauthorized account.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickLogin = async (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError(null);
    setIsLoading(true);
    try {
      await login(demoEmail, demoPass);
      router.push("/");
    } catch (err: any) {
      setError("Login failed. Check server status.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#F7F4EF] flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-[#5F8F83] text-white shadow-sm mb-1">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-[#29332F]">FraudGuard AI</h1>
          <p className="text-xs text-[#69736E] max-w-xs mx-auto">
            Intelligent Credit Card Fraud Detection & Risk Management
          </p>
        </div>

        {/* Login Card */}
        <Card className="p-6 bg-[#FFFDFC] border-[#E5DED5] shadow-sm space-y-5">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 rounded-lg bg-[#D99A9A]/20 border border-[#D99A9A] text-[#7B3030] text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-[#29332F]">Work Email</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-[#929A95] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="name@fraudguard.ai"
                  className="w-full bg-[#F7F4EF] border border-[#E5DED5] rounded-lg pl-9 pr-3 py-2 text-xs text-[#29332F] placeholder-[#929A95] focus:outline-none focus:ring-1 focus:ring-[#5F8F83] focus:border-[#5F8F83]"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-[#29332F]">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-[#929A95] absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full bg-[#F7F4EF] border border-[#E5DED5] rounded-lg pl-9 pr-3 py-2 text-xs text-[#29332F] placeholder-[#929A95] focus:outline-none focus:ring-1 focus:ring-[#5F8F83] focus:border-[#5F8F83]"
                />
              </div>
            </div>

            <Button type="submit" className="w-full text-xs font-semibold" isLoading={isLoading}>
              <span>Sign In to Platform</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
            </Button>
          </form>

          {/* 1-Click Demo Accounts */}
          <div className="pt-4 border-t border-[#E5DED5] space-y-3">
            <p className="text-[11px] font-semibold text-[#69736E] uppercase tracking-wider text-center">
              1-Click Demo Access
            </p>
            <div className="grid grid-cols-2 gap-2.5">
              <button
                type="button"
                onClick={() => handleQuickLogin("admin@fraudguard.ai", "Admin@2026")}
                className="p-2.5 rounded-lg bg-[#DCE7E1] hover:bg-[#C7D9D0] border border-[#CCD9D2] text-left transition-all group"
              >
                <div className="flex items-center gap-1.5 text-xs font-bold text-[#26332F]">
                  <ShieldCheck className="w-3.5 h-3.5 text-[#5F8F83]" />
                  <span>Admin</span>
                </div>
                <p className="text-[10px] text-[#69736E] mt-0.5">Full CRO controls</p>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin("analyst@fraudguard.ai", "Analyst@2026")}
                className="p-2.5 rounded-lg bg-[#DCE7E1] hover:bg-[#C7D9D0] border border-[#CCD9D2] text-left transition-all group"
              >
                <div className="flex items-center gap-1.5 text-xs font-bold text-[#26332F]">
                  <UserCheck className="w-3.5 h-3.5 text-[#5F8F83]" />
                  <span>Fraud Analyst</span>
                </div>
                <p className="text-[10px] text-[#69736E] mt-0.5">Triage & live queue</p>
              </button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
