import { Activity, BarChart3, HelpCircle, LayoutDashboard, Plus, Settings, History } from "lucide-react";
import { NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";

const menu = [
  { to: "/", label: "Tổng quan", icon: LayoutDashboard },
  { to: "/analysis", label: "Phân tích mới", icon: Plus },
  { to: "/history", label: "Lịch sử", icon: History },
  { to: "/reports", label: "Báo cáo", icon: BarChart3 },
  { to: "/settings", label: "Cài đặt", icon: Settings },
  { to: "/help", label: "Trợ giúp", icon: HelpCircle },
];

export function Sidebar() {
  return (
    <aside className="sidebar-shell fixed left-0 top-0 z-30 flex h-screen w-[254px] flex-col border-r border-slate-200 bg-[#f7f8fc] px-5 py-5">
      <div className="flex items-center gap-3 px-2 pb-8 pt-2">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-brand-700 text-white shadow-soft">
          <Activity className="h-8 w-8" />
        </div>
        <div>
          <div className="text-[16px] font-semibold text-brand-500">MedAI Assist</div>
        </div>
      </div>

      <nav className="flex flex-1 flex-col gap-2">
        {menu.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-2xl px-4 py-3.5 text-[15px] font-medium text-slate-700 transition hover:bg-slate-100",
                  isActive && "bg-blue-100 text-brand-600",
                )
              }
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      <div className="rounded-[22px] bg-[#eef2ff] px-4 py-4">
        <div className="text-sm text-slate-500">Phiên bản</div>
        <div className="mt-1 text-lg font-semibold text-slate-900">v1.0.0</div>
      </div>
    </aside>
  );
}
