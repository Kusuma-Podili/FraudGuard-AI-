import React from "react";
import { Card } from "./Card";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  isPositive?: boolean;
  icon?: React.ReactNode;
  subtitle?: string;
  badge?: string;
  badgeVariant?: "default" | "success" | "warning" | "danger";
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  isPositive = true,
  icon,
  subtitle,
  badge,
  badgeVariant = "default",
}) => {
  return (
    <Card className="relative overflow-hidden">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[11px] font-semibold text-[#69736E] uppercase tracking-wider">{title}</p>
          <p className="text-2xl font-bold text-[#29332F] mt-1.5 tracking-tight font-mono">{value}</p>
          {(change || subtitle) && (
            <div className="flex items-center gap-2 mt-2">
              {change && (
                <span
                  className={cn(
                    "text-[11px] font-semibold px-2 py-0.5 rounded",
                    isPositive ? "bg-[#A8C5B5]/30 text-[#35604B]" : "bg-[#D99A9A]/30 text-[#7B3030]"
                  )}
                >
                  {change}
                </span>
              )}
              {subtitle && <span className="text-[11px] text-[#929A95]">{subtitle}</span>}
            </div>
          )}
        </div>
        {icon && (
          <div className="p-2.5 bg-[#F7F4EF] rounded-xl border border-[#E5DED5] text-[#5F8F83]">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
};
