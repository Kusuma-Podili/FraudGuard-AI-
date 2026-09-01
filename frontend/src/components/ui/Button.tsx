import React from "react";
import { cn } from "@/lib/utils";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  className,
  disabled,
  ...props
}) => {
  const baseStyles =
    "inline-flex items-center justify-center font-semibold rounded-lg transition-colors focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed";

  const sizeStyles = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-4 py-2 text-xs",
    lg: "px-5 py-2.5 text-sm",
  };

  const variantStyles = {
    primary: "bg-[#FB923C] hover:bg-[#F97316] text-white shadow-sm",
    secondary: "bg-gray-100 hover:bg-gray-200 text-gray-900 border border-gray-200",
    outline: "bg-white hover:bg-gray-50 text-gray-700 border border-[#E5E7EB]",
    danger: "bg-[#FFEDD5] hover:bg-[#FED7AA] text-[#9A3412] border border-[#FDBA74]",
    ghost: "bg-transparent hover:bg-gray-100 text-gray-700",
  };

  return (
    <button
      className={cn(baseStyles, sizeStyles[size], variantStyles[variant], className)}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2" />
      ) : null}
      {children}
    </button>
  );
};
