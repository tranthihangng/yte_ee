import { cn } from "@/lib/utils";

export function Tabs({
  tabs,
  value,
  onChange,
  className,
}: {
  tabs: Array<{ value: string; label: string }>;
  value: string;
  onChange: (value: string) => void;
  className?: string;
}) {
  return (
    <div className={cn("inline-flex rounded-2xl bg-slate-100 p-1", className)}>
      {tabs.map((tab) => (
        <button
          key={tab.value}
          type="button"
          onClick={() => onChange(tab.value)}
          className={cn(
            "rounded-xl px-5 py-2.5 text-sm font-medium transition",
            value === tab.value ? "bg-brand-500 text-white shadow" : "text-slate-700 hover:bg-white",
          )}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
