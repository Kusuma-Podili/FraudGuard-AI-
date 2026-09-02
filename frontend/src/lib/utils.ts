import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number, currency: string = "INR"): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
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
        bg: "bg-[#FFEDD5]",
        text: "text-[#EA580C]",
        border: "border-[#FDBA74]",
        badge: "bg-[#FFEDD5] text-[#9A3412] border border-[#FDBA74]",
      };
    case "HIGH":
      return {
        bg: "bg-[#FFF7ED]",
        text: "text-[#C2410C]",
        border: "border-[#FED7AA]",
        badge: "bg-[#FFF7ED] text-[#C2410C] border border-[#FED7AA]",
      };
    case "MEDIUM":
      return {
        bg: "bg-gray-100",
        text: "text-gray-800",
        border: "border-gray-200",
        badge: "bg-gray-100 text-gray-800 border border-gray-300",
      };
    case "LOW":
    default:
      return {
        bg: "bg-gray-50",
        text: "text-gray-700",
        border: "border-gray-200",
        badge: "bg-gray-100 text-gray-700 border border-gray-200",
      };
  }
}

export function getActionBadge(action: string): { label: string; className: string } {
  switch (action?.toUpperCase()) {
    case "DECLINE":
      return {
        label: "DECLINED",
        className: "bg-[#FFEDD5] text-[#9A3412] border border-[#FDBA74]",
      };
    case "CHALLENGE_3DS":
      return {
        label: "3DS CHALLENGE",
        className: "bg-gray-100 text-gray-800 border border-gray-300",
      };
    case "REVIEW":
      return {
        label: "MANUAL REVIEW",
        className: "bg-[#FFF7ED] text-[#C2410C] border border-[#FED7AA]",
      };
    case "ALLOW":
    default:
      return {
        label: "APPROVED",
        className: "bg-gray-100 text-gray-800 border border-gray-200",
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
