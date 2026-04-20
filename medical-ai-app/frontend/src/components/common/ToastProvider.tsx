import { CheckCircle2, CircleAlert, Info, X } from "lucide-react";
import { createContext, ReactNode, useCallback, useContext, useMemo, useState } from "react";

type ToastType = "success" | "error" | "info";
type ToastItem = { id: number; message: string; type: ToastType };
type ToastContextType = { pushToast: (message: string, type?: ToastType) => void };

const ToastContext = createContext<ToastContextType | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);

  const pushToast = useCallback((message: string, type: ToastType = "info") => {
    const id = Date.now() + Math.floor(Math.random() * 100);
    setItems((prev: ToastItem[]) => [...prev, { id, message, type }]);
    window.setTimeout(() => setItems((prev: ToastItem[]) => prev.filter((t: ToastItem) => t.id !== id)), 3200);
  }, []);

  const value = useMemo(() => ({ pushToast }), [pushToast]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed right-5 top-5 z-50 space-y-2">
        {items.map((item) => (
          <div
            key={item.id}
            className={`pointer-events-auto flex min-w-[280px] items-center justify-between rounded-xl border px-3 py-2 text-sm shadow-lg ${
              item.type === "success"
                ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                : item.type === "error"
                  ? "border-red-200 bg-red-50 text-red-700"
                  : "border-blue-200 bg-blue-50 text-blue-700"
            }`}
          >
            <div className="flex items-center gap-2">
              {item.type === "success" ? <CheckCircle2 className="h-4 w-4" /> : item.type === "error" ? <CircleAlert className="h-4 w-4" /> : <Info className="h-4 w-4" />}
              <span>{item.message}</span>
            </div>
            <button className="ml-3" onClick={() => setItems((prev: ToastItem[]) => prev.filter((t: ToastItem) => t.id !== item.id))}>
              <X className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}
