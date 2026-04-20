import { Download, Filter, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { toast } from "sonner";
import { EmptyState } from "@/components/common/EmptyState";
import { LoadingState } from "@/components/common/LoadingState";
import { StatusDonutChart } from "@/components/charts/StatusDonutChart";
import { HistoryTable } from "@/components/history/HistoryTable";
import { Pagination } from "@/components/history/Pagination";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { fetchCases, getCasesCsvUrl } from "@/services/caseService";
import type { CaseItem } from "@/types/case";

export default function HistoryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [items, setItems] = useState<CaseItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const page = Number(searchParams.get("page") || 1);
  const pageSize = 8;
  const search = searchParams.get("search") || "";
  const moduleType = searchParams.get("module_type") || "";
  const status = searchParams.get("status") || "";
  const dateFrom = searchParams.get("date_from") || "";
  const dateTo = searchParams.get("date_to") || "";

  const [filters, setFilters] = useState({
    search,
    moduleType,
    status,
    dateFrom,
    dateTo,
  });

  useEffect(() => {
    setLoading(true);
    fetchCases({
      page,
      page_size: pageSize,
      search: search || undefined,
      module_type: moduleType || undefined,
      status: status || undefined,
      date_from: dateFrom || undefined,
      date_to: dateTo || undefined,
    })
      .then((response) => {
        setItems(response.items);
        setTotal(response.total);
      })
      .catch((error) => toast.error(error instanceof Error ? error.message : "Không tải được lịch sử"))
      .finally(() => setLoading(false));
  }, [page, pageSize, search, moduleType, status, dateFrom, dateTo]);

  const statusStats = useMemo(() => {
    const saved = items.filter((item) => item.status === "saved").length;
    const pending = items.filter((item) => item.status === "pending_confirmation").length;
    const error = items.filter((item) => item.status === "error").length;
    return { saved, pending, error };
  }, [items]);

  const applyFilters = () => {
    const next = new URLSearchParams();
    if (filters.search) next.set("search", filters.search);
    if (filters.moduleType) next.set("module_type", filters.moduleType);
    if (filters.status) next.set("status", filters.status);
    if (filters.dateFrom) next.set("date_from", filters.dateFrom);
    if (filters.dateTo) next.set("date_to", filters.dateTo);
    next.set("page", "1");
    setSearchParams(next);
  };

  const resetFilters = () => {
    setFilters({ search: "", moduleType: "", status: "", dateFrom: "", dateTo: "" });
    setSearchParams({ page: "1" });
  };

  if (loading) return <LoadingState />;

  return (
    <div className="space-y-6">
      <h1 className="text-[28px] font-bold text-slate-900">Lịch sử ca bệnh</h1>

      <Card>
        <CardContent className="grid grid-cols-[1fr_0.9fr_1.1fr_0.8fr_auto] gap-4 pt-6">
          <div>
            <label className="mb-2 block text-sm text-slate-500">Mã ca</label>
            <Input value={filters.search} onChange={(event) => setFilters((prev) => ({ ...prev, search: event.target.value }))} placeholder="Nhập mã ca..." />
          </div>
          <div>
            <label className="mb-2 block text-sm text-slate-500">Loại mô-đun</label>
            <Select
              value={filters.moduleType}
              onChange={(value) => setFilters((prev) => ({ ...prev, moduleType: value }))}
              options={[
                { value: "", label: "Tất cả" },
                { value: "brain_mri", label: "Brain MRI" },
                { value: "histopath", label: "Histopath" },
                { value: "wrist_xray", label: "Wrist X-ray" },
              ]}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-2 block text-sm text-slate-500">Từ ngày</label>
              <Input type="date" value={filters.dateFrom} onChange={(event) => setFilters((prev) => ({ ...prev, dateFrom: event.target.value }))} />
            </div>
            <div>
              <label className="mb-2 block text-sm text-slate-500">Đến ngày</label>
              <Input type="date" value={filters.dateTo} onChange={(event) => setFilters((prev) => ({ ...prev, dateTo: event.target.value }))} />
            </div>
          </div>
          <div>
            <label className="mb-2 block text-sm text-slate-500">Trạng thái</label>
            <Select
              value={filters.status}
              onChange={(value) => setFilters((prev) => ({ ...prev, status: value }))}
              options={[
                { value: "", label: "Tất cả" },
                { value: "saved", label: "Đã lưu" },
                { value: "pending_confirmation", label: "Chờ xác nhận" },
                { value: "error", label: "Lỗi xử lý" },
              ]}
            />
          </div>
          <div className="flex items-end gap-3">
            <Button onClick={applyFilters}>
              <Filter className="h-4 w-4" />
              Lọc
            </Button>
            <Button variant="outline" onClick={resetFilters}>
              <RotateCcw className="h-4 w-4" />
              Đặt lại
            </Button>
            <a href={getCasesCsvUrl({
              search: search || undefined,
              module_type: moduleType || undefined,
              status: status || undefined,
              date_from: dateFrom || undefined,
              date_to: dateTo || undefined,
            })}>
              <Button variant="outline">
                <Download className="h-4 w-4" />
                Xuất CSV
              </Button>
            </a>
          </div>
        </CardContent>
      </Card>

      {items.length === 0 ? <EmptyState text="Không có ca bệnh phù hợp bộ lọc." /> : <HistoryTable items={items} />}

      <Pagination page={page} total={total} pageSize={pageSize} onPageChange={(nextPage) => {
        const next = new URLSearchParams(searchParams);
        next.set("page", String(nextPage));
        setSearchParams(next);
      }} />

      <div className="grid grid-cols-[1.2fr_0.9fr] gap-5">
        <div className="grid grid-cols-3 gap-5">
          <Card><CardContent className="pt-6"><div className="text-sm text-slate-500">Tổng số ca</div><div className="mt-2 text-[22px] font-bold text-slate-900">{total}</div></CardContent></Card>
          <Card className="bg-emerald-50/40"><CardContent className="pt-6"><div className="text-sm text-slate-500">Đã lưu</div><div className="mt-2 text-[22px] font-bold text-emerald-600">{statusStats.saved}</div></CardContent></Card>
          <Card className="bg-amber-50/40"><CardContent className="pt-6"><div className="text-sm text-slate-500">Chờ xác nhận</div><div className="mt-2 text-[22px] font-bold text-amber-600">{statusStats.pending}</div></CardContent></Card>
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Phân bố trạng thái</CardTitle>
          </CardHeader>
          <CardContent>
            <StatusDonutChart saved={statusStats.saved} pending={statusStats.pending} error={statusStats.error} total={Math.max(total, 1)} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
