import { Inbox } from "lucide-react";

export function EmptyState({ text = "Chưa có dữ liệu phù hợp." }: { text?: string }) {
  return (
    <div className="flex min-h-[220px] flex-col items-center justify-center gap-3 rounded-[26px] border border-dashed border-slate-200 bg-white text-slate-500 shadow-soft">
      <Inbox className="h-8 w-8" />
      <p>{text}</p>
    </div>
  );
}
