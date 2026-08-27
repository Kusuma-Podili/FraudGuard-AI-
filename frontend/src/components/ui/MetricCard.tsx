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
    <Card className="relative overflow-hidden group">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">{title}</p>
          <p className="text-2xl font-bold text-gray-100 mt-2 tracking-tight">{value}</p>
          {(change || subtitle) && (
            <div className="flex items-center gap-2 mt-2">
              {change && (
                <span
                  className={cn(
                    "text-xs font-semibold px-1.5 py-0.5 rounded",
                    isPositive ? "bg-emerald-950/60 text-emerald-400" : "bg-red-950/60 text-red-400"
                  )}
                >
                  {change}
                </span>
              )}
              {subtitle && <span className="text-xs text-gray-500">{subtitle}</span>}
            </div>
          )}
        </div>
        {icon && (
          <div className="p-3 bg-gray-800/80 rounded-xl border border-gray-700/60 text-blue-400 group-hover:text-blue-300 transition-colors">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
};
