import { AlertTriangle, Check, Clock } from "lucide-react";
import { formatStatus } from "@/lib/utils";

export function StatusBadge({ status }: { status: string }) {
  if (status === "saved") {
    return (
      <span className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1 text-sm font-medium text-emerald-700">
        <Check className="h-4 w-4" />
        {formatStatus(status)}
      </span>
    );
  }
  if (status === "pending_confirmation") {
    return (
      <span className="inline-flex items-center gap-2 rounded-full bg-amber-50 px-3 py-1 text-sm font-medium text-amber-700">
        <Clock className="h-4 w-4" />
        {formatStatus(status)}
      </span>
    );
  }
  if (status === "error") {
    return (
      <span className="inline-flex items-center gap-2 rounded-full bg-rose-50 px-3 py-1 text-sm font-medium text-rose-700">
        <AlertTriangle className="h-4 w-4" />
        {formatStatus(status)}
      </span>
    );
  }
  return <span className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-700">{formatStatus(status)}</span>;
}
