import React from "react";
import { cn } from "@/lib/utils";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "danger" | "purple" | "outline";
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  className,
  variant = "default",
  ...props
}) => {
  const variants = {
    default: "bg-gray-800 text-gray-300 border-gray-700",
    success: "bg-emerald-950/60 text-emerald-400 border-emerald-500/30",
    warning: "bg-amber-950/60 text-amber-400 border-amber-500/30",
    danger: "bg-red-950/60 text-red-400 border-red-500/30",
    purple: "bg-purple-950/60 text-purple-400 border-purple-500/30",
    outline: "bg-transparent text-gray-400 border-gray-700",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};
