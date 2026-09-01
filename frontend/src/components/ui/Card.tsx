import React from "react";
import { cn } from "@/lib/utils";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, className, hover = false, ...props }) => {
  return (
    <div
      className={cn(
        "bg-[#FFFDFC] border border-[#E5DED5] rounded-xl p-5 shadow-[0_1px_3px_rgba(41,51,47,0.04)]",
        hover && "hover:border-[#CCD9D2] hover:shadow-[0_2px_6px_rgba(41,51,47,0.07)] transition-all",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ children, className, ...props }) => (
  <div className={cn("flex items-center justify-between pb-3.5 mb-3.5 border-b border-[#E5DED5]", className)} {...props}>
    {children}
  </div>
);

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ children, className, ...props }) => (
  <h3 className={cn("text-base font-bold text-[#29332F] tracking-tight", className)} {...props}>
    {children}
  </h3>
);

export const CardDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({ children, className, ...props }) => (
  <p className={cn("text-xs text-[#69736E] mt-0.5", className)} {...props}>
    {children}
  </p>
);
