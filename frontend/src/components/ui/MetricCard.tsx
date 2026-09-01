import React from "react";
import { Card } from "./Card";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  isPositive?: boolean;
  subtitle?: string;
  icon?: React.ReactNode;
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  isPositive,
  subtitle,
  icon,
  className,
}) => {
  return (
    <Card className={cn("p-5 bg-white border border-[#E5E7EB] space-y-1.5", className)}>
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider">
          {title}
        </span>
        {icon && (
          <div className="w-7 h-7 rounded-lg bg-gray-100 flex items-center justify-center text-gray-700">
            {icon}
          </div>
        )}
      </div>

      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-bold text-gray-900 tracking-tight font-mono">{value}</span>
      </div>

      {change && (
        <p className="text-[11px] font-medium text-gray-600">
          {change}
        </p>
      )}

      {subtitle && !change && (
        <p className="text-[11px] text-gray-400">{subtitle}</p>
      )}
    </Card>
  );
};
