import { Bell, ChevronDown, Search } from "lucide-react";

export function Header() {
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
        <div className="h-10 w-10 rounded-full bg-blue-600 text-white grid place-items-center font-semibold">NT</div>
        <div>
          <div className="text-sm font-semibold">Nguyễn Thị An</div>
          <div className="text-xs text-slate-500">Bác sĩ / Quản trị viên</div>
        </div>
        <ChevronDown className="h-4 w-4 text-slate-500" />
      </div>
    </header>
  );
}
