import { Bell, ChevronDown, Search } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../../store/authStore";

export function Header() {
  const user = useAuthStore((state) => state.user);
  const clearAuth = useAuthStore((state) => state.clearAuth);
  const navigate = useNavigate();

  const initials = user?.full_name
    ?.split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("") || "US";

  const handleLogout = () => {
    clearAuth();
    navigate("/login", { replace: true });
  };

  return (
    <header className="sticky top-0 z-10 flex h-20 items-center justify-between border-b border-slate-200 bg-[#f3f6fb]/95 px-6 backdrop-blur">
      <div className="relative w-[420px]">
        <Search className="absolute left-3 top-3.5 h-4 w-4 text-slate-400" />
        <input
          className="h-11 w-full rounded-xl border border-slate-200 bg-white pl-10 pr-4 text-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
          placeholder="Tìm kiếm ca bệnh..."
        />
      </div>
      <div className="flex items-center gap-4">
        <button className="relative rounded-full p-2 hover:bg-white">
          <Bell className="h-5 w-5 text-slate-600" />
          <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-red-500" />
        </button>
        <div className="grid h-10 w-10 place-items-center rounded-full bg-blue-600 font-semibold text-white">{initials}</div>
        <div>
          <div className="text-sm font-semibold">{user?.full_name || "Người dùng"}</div>
          <div className="text-xs text-slate-500">{user?.role || "user"}</div>
        </div>
        <ChevronDown className="h-4 w-4 text-slate-500" />
        <button className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm hover:bg-white" onClick={handleLogout}>
          Đăng xuất
        </button>
      </div>
    </header>
  );
}
