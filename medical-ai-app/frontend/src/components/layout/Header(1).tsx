import { Bell, ChevronDown, Search } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { useAppStore } from "@/store/appStore";

export function Header() {
  const navigate = useNavigate();
  const { searchText, setSearchText } = useAppStore();
  const [value, setValue] = useState(searchText);

  return (
    <header className="header-shell fixed left-[254px] right-0 top-0 z-20 flex h-[86px] items-center justify-between border-b border-slate-200 bg-[#f7f8fc]/95 px-8 backdrop-blur-sm">
      <div className="relative max-w-[420px] flex-1">
        <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
        <Input
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              setSearchText(value);
              navigate(`/history?search=${encodeURIComponent(value)}`);
            }
          }}
          className="h-12 rounded-2xl bg-white pl-12 text-[15px]"
          placeholder="Tìm kiếm ca bệnh..."
        />
      </div>

      <div className="ml-6 flex items-center gap-6">
        <div className="relative">
          <Bell className="h-7 w-7 text-slate-600" />
          <span className="absolute right-0 top-0 h-3 w-3 rounded-full bg-rose-500" />
        </div>
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-brand-500 text-lg font-semibold text-white">NT</div>
          <div className="leading-tight">
            <div className="text-[16px] font-semibold text-slate-900">Nguyễn Thị An</div>
            <div className="text-sm text-slate-500">Bác sĩ / Quản trị viên</div>
          </div>
          <ChevronDown className="h-5 w-5 text-slate-500" />
        </div>
      </div>
    </header>
  );
}
