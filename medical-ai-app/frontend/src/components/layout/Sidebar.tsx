import { BarChart3, CircleHelp, Cog, LayoutGrid, Plus, RotateCcw, Stethoscope } from "lucide-react";
import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Tổng quan", icon: LayoutGrid },
  { to: "/analysis", label: "Phân tích mới", icon: Plus },
  { to: "/history", label: "Lịch sử", icon: RotateCcw },
  { to: "/reports", label: "Báo cáo", icon: BarChart3 },
  { to: "/settings", label: "Cài đặt", icon: Cog },
  { to: "/help", label: "Trợ giúp", icon: CircleHelp }
];

export function Sidebar() {
  return (
    <aside className="w-64 min-h-screen border-r border-slate-200 bg-[#f7faff] p-4">
      <div className="mb-8 flex items-center gap-3 px-2 pt-2">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-blue-600 text-white shadow-md">
          <Stethoscope className="h-5 w-5" />
        </div>
        <div className="text-xl font-bold text-blue-700">MedAI Assist</div>
      </div>
      <nav className="space-y-1.5">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm ${isActive ? "bg-blue-100 text-blue-700" : "text-slate-700 hover:bg-slate-100"}`
            }
          >
            <link.icon className="h-4 w-4" />
            {link.label}
          </NavLink>
        ))}
      </nav>
      <div className="mt-10 rounded-xl border bg-white p-3 text-sm text-slate-600 shadow-sm">
        <div className="font-semibold">Phiên bản</div>
        <div>v1.0.0</div>
      </div>
    </aside>
  );
}
