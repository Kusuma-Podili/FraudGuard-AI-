"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  className,
  variant = "primary",
  size = "md",
  isLoading = false,
  disabled,
  ...props
}) => {
  const baseStyles = "inline-flex items-center justify-center font-semibold rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed";

  const variants = {
    primary: "bg-[#5F8F83] hover:bg-[#4F7D72] text-white shadow-sm focus:ring-[#5F8F83]",
    secondary: "bg-[#DCE7E1] hover:bg-[#C7D9D0] text-[#26332F] border border-[#CCD9D2] focus:ring-[#5F8F83]",
    danger: "bg-[#D99A9A]/30 hover:bg-[#D99A9A]/50 text-[#7B3030] border border-[#D99A9A] focus:ring-[#D99A9A]",
    outline: "bg-[#FFFDFC] border border-[#E5DED5] hover:bg-[#F7F4EF] text-[#29332F] focus:ring-[#5F8F83]",
    ghost: "text-[#69736E] hover:text-[#29332F] hover:bg-[#DCE7E1]/40",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-4 py-2 text-sm",
    lg: "px-5 py-2.5 text-base",
  };

  return (
    <button
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="inline-flex items-center gap-2">
          <svg className="animate-spin h-3.5 w-3.5 text-current" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
          Loading...
        </span>
      ) : (
        children
      )}
    </button>
  );
};
