export function LoadingState({ text = "Đang tải dữ liệu..." }: { text?: string }) {
  return (
    <div className="flex min-h-[220px] items-center justify-center rounded-[26px] border border-dashed border-slate-200 bg-white text-slate-500 shadow-soft">
      {text}
    </div>
  );
}
