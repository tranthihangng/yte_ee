import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Badge({
  className,
  children,
  tone = "blue",
}: {
  className?: string;
  children: ReactNode;
  tone?: "blue" | "green" | "purple" | "amber" | "slate";
}) {
  const toneMap = {
    blue: "bg-blue-100 text-blue-700",
    green: "bg-emerald-100 text-emerald-700",
    purple: "bg-violet-100 text-violet-700",
    amber: "bg-amber-100 text-amber-700",
    slate: "bg-slate-100 text-slate-700",
  };
  return <span className={cn("inline-flex rounded-full px-3 py-1 text-xs font-semibold", toneMap[tone], className)}>{children}</span>;
}
