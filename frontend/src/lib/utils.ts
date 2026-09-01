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
  switch (tier?.toUpperCase()) {
    case "CRITICAL":
      return {
        bg: "bg-[#D99A9A]/20",
        text: "text-[#7B3030]",
        border: "border-[#D99A9A]/60",
        badge: "bg-[#D99A9A] text-[#7B3030] border border-[#C98A8A]",
      };
    case "HIGH":
      return {
        bg: "bg-[#E8A98A]/20",
        text: "text-[#8A472E]",
        border: "border-[#E8A98A]/60",
        badge: "bg-[#E8A98A] text-[#8A472E] border border-[#D8997A]",
      };
    case "MEDIUM":
      return {
        bg: "bg-[#E8C98A]/20",
        text: "text-[#795B20]",
        border: "border-[#E8C98A]/60",
        badge: "bg-[#E8C98A] text-[#795B20] border border-[#D8B97A]",
      };
    case "LOW":
    default:
      return {
        bg: "bg-[#A8C5B5]/20",
        text: "text-[#35604B]",
        border: "border-[#A8C5B5]/60",
        badge: "bg-[#A8C5B5] text-[#35604B] border border-[#98B5A5]",
      };
  }
}

export function getActionBadge(action: string): { label: string; className: string } {
  switch (action?.toUpperCase()) {
    case "DECLINE":
      return {
        label: "DECLINED",
        className: "bg-[#D99A9A]/30 text-[#7B3030] border border-[#D99A9A]",
      };
    case "CHALLENGE_3DS":
      return {
        label: "3DS CHALLENGE",
        className: "bg-[#A99BBE]/30 text-[#4C3B66] border border-[#A99BBE]",
      };
    case "REVIEW":
      return {
        label: "MANUAL REVIEW",
        className: "bg-[#E8C98A]/30 text-[#795B20] border border-[#E8C98A]",
      };
    case "ALLOW":
    default:
      return {
        label: "APPROVED",
        className: "bg-[#A8C5B5]/30 text-[#35604B] border border-[#A8C5B5]",
      };
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
