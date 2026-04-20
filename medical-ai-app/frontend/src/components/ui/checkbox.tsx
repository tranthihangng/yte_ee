export function Checkbox({
  checked,
  onChange,
}: {
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className={`flex h-5 w-5 items-center justify-center rounded border ${checked ? "border-brand-500 bg-brand-500 text-white" : "border-slate-300 bg-white"}`}
    >
      {checked ? "✓" : ""}
    </button>
  );
}
