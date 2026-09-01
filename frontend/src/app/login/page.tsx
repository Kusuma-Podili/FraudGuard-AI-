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
    <div className="min-h-screen w-full bg-[#FAFAFA] flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-[#FFEDD5] text-[#EA580C] border border-[#FDBA74] shadow-sm mb-1">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-[#111827]">FraudGuard AI</h1>
          <p className="text-xs text-[#4B5563] max-w-xs mx-auto">
            Intelligent Credit Card Fraud Detection & Risk Management
          </p>
        </div>

        {/* Login Card */}
        <Card className="p-6 bg-white border-[#E5E7EB] shadow-sm space-y-5">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 rounded-lg bg-[#FFEDD5] border border-[#FDBA74] text-[#9A3412] text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-[#111827]">Work Email</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="name@fraudguard.ai"
                  className="w-full bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg pl-9 pr-3 py-2 text-xs text-[#111827] placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-[#FB923C] focus:border-[#FB923C]"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-[#111827]">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg pl-9 pr-3 py-2 text-xs text-[#111827] placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-[#FB923C] focus:border-[#FB923C]"
                />
              </div>
            </div>

            <Button type="submit" className="w-full text-xs font-semibold" isLoading={isLoading}>
              <span>Sign In to Platform</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
            </Button>
          </form>

          {/* 1-Click Demo Accounts */}
          <div className="pt-4 border-t border-[#E5E7EB] space-y-3">
            <p className="text-[11px] font-semibold text-[#4B5563] uppercase tracking-wider text-center">
              1-Click Demo Access
            </p>
            <div className="grid grid-cols-2 gap-2.5">
              <button
                type="button"
                onClick={() => handleQuickLogin("admin@fraudguard.ai", "Admin@2026")}
                className="p-2.5 rounded-lg bg-[#F9FAFB] hover:bg-[#FFF7ED] border border-[#E5E7EB] text-left transition-all group"
              >
                <div className="flex items-center gap-1.5 text-xs font-bold text-[#111827]">
                  <ShieldCheck className="w-3.5 h-3.5 text-[#EA580C]" />
                  <span>Admin</span>
                </div>
                <p className="text-[10px] text-[#4B5563] mt-0.5">Full CRO controls</p>
              </button>

              <button
                type="button"
                onClick={() => handleQuickLogin("analyst@fraudguard.ai", "Analyst@2026")}
                className="p-2.5 rounded-lg bg-[#F9FAFB] hover:bg-[#FFF7ED] border border-[#E5E7EB] text-left transition-all group"
              >
                <div className="flex items-center gap-1.5 text-xs font-bold text-[#111827]">
                  <UserCheck className="w-3.5 h-3.5 text-[#EA580C]" />
                  <span>Fraud Analyst</span>
                </div>
                <p className="text-[10px] text-[#4B5563] mt-0.5">Triage & live queue</p>
              </button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
