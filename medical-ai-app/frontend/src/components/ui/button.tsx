import * as React from "react";
import { cn } from "@/lib/utils";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "default" | "outline" | "ghost" | "secondary";
  size?: "default" | "sm" | "lg" | "icon";
};

export function Button({
  className,
  variant = "default",
  size = "default",
  ...props
}: ButtonProps) {
  const variants: Record<string, string> = {
    default: "bg-brand-500 text-white hover:bg-brand-600 border border-brand-500",
    outline: "bg-white text-brand-600 border border-brand-200 hover:bg-brand-50",
    ghost: "bg-transparent text-slate-700 hover:bg-slate-100 border border-transparent",
    secondary: "bg-slate-100 text-slate-800 hover:bg-slate-200 border border-slate-200",
  };
  const sizes: Record<string, string> = {
    default: "h-11 px-5 text-sm",
    sm: "h-9 px-3 text-sm",
    lg: "h-12 px-6 text-base",
    icon: "h-10 w-10",
  };

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-2xl font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-60",
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    />
  );
}
