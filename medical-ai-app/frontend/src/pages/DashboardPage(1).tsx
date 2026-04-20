import { Activity, CalendarDays, ClipboardList, Package } from "lucide-react";
import { useEffect, useState } from "react";
import { fetchDashboardSummary, fetchRecentCases } from "@/services/dashboardService";
import type { DashboardSummary, RecentCase } from "@/types/dashboard";
import { LoadingState } from "@/components/common/LoadingState";
import { EmptyState } from "@/components/common/EmptyState";
import { ModuleCard } from "@/components/dashboard/ModuleCard";
import { NotificationsCard } from "@/components/dashboard/NotificationsCard";
import { PerformanceCard } from "@/components/dashboard/PerformanceCard";
import { RecentCasesCard } from "@/components/dashboard/RecentCasesCard";
import { StatCard } from "@/components/dashboard/StatCard";
import { UsageTipsCard } from "@/components/dashboard/UsageTipsCard";

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [recentCases, setRecentCases] = useState<RecentCase[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchDashboardSummary(), fetchRecentCases(5)])
      .then(([summaryData, recentData]) => {
        setSummary(summaryData);
        setRecentCases(recentData);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingState />;

  if (!summary) return <EmptyState text="Không tải được dữ liệu dashboard." />;

  return (
    <div className="space-y-6">
      <h1 className="text-[28px] font-bold text-slate-900">Bảng điều khiển</h1>

      <div className="grid grid-cols-4 gap-5">
        <StatCard icon={ClipboardList} label="Tổng số ca" value={summary.total_cases.toLocaleString("vi-VN")} tone="blue" />
        <StatCard icon={CalendarDays} label="Ca hôm nay" value={summary.today_cases.toString()} tone="green" />
        <StatCard icon={Activity} label="Độ chính xác TB" value={`${summary.average_accuracy}%`} tone="amber" />
        <StatCard icon={Package} label="Mô-đun đang hoạt động" value={summary.active_modules.toString()} tone="purple" />
      </div>

      <section className="space-y-4">
        <h2 className="text-[18px] font-semibold text-slate-900">Chọn mô-đun phân tích</h2>
        <div className="grid grid-cols-3 gap-5">
          <ModuleCard moduleType="brain_mri" badge="MRI" title="Brain MRI Segmentation" description="Phân đoạn khối u não trên ảnh MRI" />
          <ModuleCard moduleType="histopath" badge="Pathology" title="Histopathology Classification" description="Phân loại ảnh mô bệnh học" />
          <ModuleCard moduleType="wrist_xray" badge="X-ray" title="Wrist X-ray Detection" description="Phát hiện gãy xương / kim loại" />
        </div>
      </section>

      <div className="grid grid-cols-[1.35fr_0.95fr] gap-5">
        <RecentCasesCard items={recentCases} />
        <PerformanceCard averageAccuracy={summary.average_accuracy} performance={summary.performance} />
      </div>

      <div className="grid grid-cols-2 gap-5">
        <UsageTipsCard tips={summary.quick_tips} />
        <NotificationsCard items={summary.notifications} />
      </div>
    </div>
  );
}
