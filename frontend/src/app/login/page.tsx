"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { ShieldCheck, Lock, Mail, ArrowRight, ShieldAlert, UserCheck, AlertCircle } from "lucide-react";
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
    <div className="min-h-screen w-full bg-[#070B14] flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Ambient background glow */}
      <div className="absolute w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-3xl -top-40 -left-40 pointer-events-none" />
      <div className="absolute w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-3xl -bottom-32 -right-32 pointer-events-none" />

      <div className="w-full max-w-md space-y-6 relative z-10">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 shadow-xl shadow-blue-500/25 ring-1 ring-white/20 mb-2">
            <ShieldCheck className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">FRAUDGUARD AI</h1>
          <p className="text-xs text-gray-400 max-w-xs mx-auto">
            Sub-20ms Credit Card Fraud Detection & Risk Management Platform
          </p>
        </div>

        {/* Login Card */}
        <Card className="bg-[#0B1220]/90 border-gray-800 backdrop-blur-xl p-6 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 rounded-lg bg-red-950/60 border border-red-500/30 text-red-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
                <span>{error}</span>
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-300">Work Email</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="name@fraudguard.ai"
                  className="w-full bg-gray-900/80 border border-gray-800 rounded-lg pl-9 pr-3 py-2 text-xs text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-300">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full bg-gray-900/80 border border-gray-800 rounded-lg pl-9 pr-3 py-2 text-xs text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <Button type="submit" disabled={isLoading} className="w-full mt-2" size="md">
              {isLoading ? "Authenticating..." : "Sign In to Console"}
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </form>

          {/* Quick Demo Access Bar */}
          <div className="mt-6 pt-5 border-t border-gray-800/80 space-y-2.5">
            <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider block text-center">
              1-Click Demo Accounts
            </span>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin("admin@fraudguard.ai", "Admin@2026")}
                className="flex items-center justify-center gap-1.5 p-2 bg-blue-950/60 hover:bg-blue-900/60 border border-blue-500/30 rounded-lg text-xs font-semibold text-blue-300 transition-all"
              >
                <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
                <span>Admin Login</span>
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin("analyst@fraudguard.ai", "Analyst@2026")}
                className="flex items-center justify-center gap-1.5 p-2 bg-emerald-950/60 hover:bg-emerald-900/60 border border-emerald-500/30 rounded-lg text-xs font-semibold text-emerald-300 transition-all"
              >
                <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>Analyst Login</span>
              </button>
            </div>
          </div>
        </Card>

        {/* Security badge */}
        <div className="text-center">
          <p className="text-[11px] text-gray-500 font-mono">
            PCI-DSS v4.0 Level 1 Compliant • TLS 1.3 End-to-End Encrypted
          </p>
        </div>
      </div>
    </div>
  );
}
