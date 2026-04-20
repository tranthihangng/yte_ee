import { Outlet } from "react-router-dom";
import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";

export function AppLayout() {
  return (
    <div className="min-h-screen bg-appbg">
      <Sidebar />
      <Header />
      <main className="min-h-screen pl-[254px] pt-[86px]">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
