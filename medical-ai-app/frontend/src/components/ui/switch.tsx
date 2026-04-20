export function Switch({
  checked,
  onCheckedChange,
}: {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onCheckedChange(!checked)}
      className={`relative inline-flex h-7 w-12 items-center rounded-full transition ${checked ? "bg-emerald-500" : "bg-slate-300"}`}
    >
      <span
        className={`inline-block h-5 w-5 rounded-full bg-white transition ${checked ? "translate-x-6" : "translate-x-1"}`}
      />
    </button>
  );
}
