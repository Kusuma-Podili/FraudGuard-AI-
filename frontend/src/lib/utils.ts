import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number, currency: string = "USD"): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatRiskScore(score: number): string {
  return (score * 100).toFixed(1) + "%";
}

export function getRiskColor(tier: string): { bg: string; text: string; border: string; badge: string } {
  switch (tier) {
    case "CRITICAL":
      return { bg: "bg-red-950/40", text: "text-red-400", border: "border-red-500/30", badge: "bg-red-500 text-white" };
    case "HIGH":
      return { bg: "bg-orange-950/40", text: "text-orange-400", border: "border-orange-500/30", badge: "bg-orange-500 text-white" };
    case "MEDIUM":
      return { bg: "bg-amber-950/40", text: "text-amber-400", border: "border-amber-500/30", badge: "bg-amber-500 text-white" };
    case "LOW":
    default:
      return { bg: "bg-emerald-950/40", text: "text-emerald-400", border: "border-emerald-500/30", badge: "bg-emerald-500 text-white" };
  }
}

export function getActionBadge(action: string): { label: string; className: string } {
  switch (action) {
    case "DECLINE":
      return { label: "DECLINED", className: "bg-red-500/20 text-red-400 border border-red-500/40" };
    case "CHALLENGE_3DS":
      return { label: "3DS CHALLENGE", className: "bg-purple-500/20 text-purple-400 border border-purple-500/40" };
    case "REVIEW":
      return { label: "MANUAL REVIEW", className: "bg-amber-500/20 text-amber-400 border border-amber-500/40" };
    case "ALLOW":
    default:
      return { label: "APPROVED", className: "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40" };
  }
}

export function formatTimeAgo(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffSec = Math.max(0, Math.floor((now.getTime() - date.getTime()) / 1000));

  if (diffSec < 5) return "just now";
  if (diffSec < 60) return `${diffSec}s ago`;
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHours = Math.floor(diffMin / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${Math.floor(diffHours / 24)}d ago`;
}
