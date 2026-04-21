import { useEffect, useMemo, useState } from "react";
import { CircleCheck, CircleDashed, CircleX, Download, Eye, Filter, RotateCcw } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useToast } from "../components/common/ToastProvider";
import { caseService } from "../services/caseService";

export function HistoryPage() {
  const navigate = useNavigate();
  const { pushToast } = useToast();
  const [items, setItems] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [q, setQ] = useState("");
  const [module, setModule] = useState("all");
  const [status, setStatus] = useState("all");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const load = () => {
    setLoading(true);
    setError("");
    caseService
      .getCases({ page, page_size: 8, q, module, status, from_date: fromDate, to_date: toDate })
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
      })
      .catch(() => {
        setError("Không tải được lịch sử ca bệnh");
        pushToast("Lỗi tải lịch sử", "error");
      })
      .finally(() => setLoading(false));
  };
  useEffect(() => {
    load();
  }, [page]);

  const exportCsv = async () => {
    try {
      const blob = await caseService.exportCsv({ q, module, status, from_date: fromDate, to_date: toDate });
      const url = URL.createObjectURL(new Blob([blob]));
      const a = document.createElement("a");
      a.href = url;
      a.download = "cases.csv";
      a.click();
      pushToast("Xuất CSV thành công", "success");
    } catch {
      pushToast("Xuất CSV thất bại", "error");
    }
  };

  const resetFilter = () => {
    setQ("");
    setModule("all");
    setStatus("all");
    setFromDate("");
    setToDate("");
    setPage(1);
  };

  const quickStat = useMemo(() => {
    const saved = items.filter((i) => String(i.status).includes("Đã lưu")).length;
    const pending = items.filter((i) => String(i.status).includes("Chờ")).length;
    const failed = items.filter((i) => String(i.status).includes("Lỗi")).length;
    return { saved, pending, failed };
  }, [items]);

  const statusBadge = (raw: string) => {
    if (raw.includes("Lỗi")) return <span className="status-pill bg-red-100 text-red-700"><CircleX className="h-3.5 w-3.5" /> Lỗi xử lý</span>;
    if (raw.includes("Chờ")) return <span className="status-pill bg-amber-100 text-amber-700"><CircleDashed className="h-3.5 w-3.5" /> Chờ xác nhận</span>;
    return <span className="status-pill bg-emerald-100 text-emerald-700"><CircleCheck className="h-3.5 w-3.5" /> Đã lưu</span>;
  };

  return (
    <div className="space-y-4">
      <h1 className="section-title text-[42px]">Lịch sử ca bệnh</h1>
      {error && <div className="card border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      <div className="card p-4">
        <div className="grid grid-cols-12 gap-3">
          <div className="col-span-2">
            <div className="mb-1 text-xs font-medium text-slate-500">Mã ca</div>
            <input className="input-base" placeholder="Nhập mã ca..." value={q} onChange={(e) => setQ(e.target.value)} />
          </div>
          <div className="col-span-2">
            <div className="mb-1 text-xs font-medium text-slate-500">Loại mô-đun</div>
            <select className="input-base" value={module} onChange={(e) => setModule(e.target.value)}>
              <option value="all">Tất cả</option><option value="brain_mri">Brain MRI</option><option value="histopath">Histopath</option><option value="wrist_xray">Wrist X-ray</option><option value="tuberculosis_counting">Tuberculosis Counting</option>
            </select>
          </div>
          <div className="col-span-3">
            <div className="mb-1 text-xs font-medium text-slate-500">Khoảng thời gian</div>
            <div className="grid grid-cols-2 gap-2">
              <input className="input-base" type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} />
              <input className="input-base" type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} />
            </div>
          </div>
          <div className="col-span-2">
            <div className="mb-1 text-xs font-medium text-slate-500">Trạng thái</div>
            <select className="input-base" value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="all">Tất cả</option><option value="Đã lưu">Đã lưu</option><option value="Chờ xác nhận">Chờ xác nhận</option><option value="Lỗi xử lý">Lỗi xử lý</option>
            </select>
          </div>
          <div className="col-span-3 flex items-end justify-end gap-2">
            <button className="inline-flex h-11 items-center gap-2 rounded-xl bg-blue-600 px-4 text-white" onClick={load}><Filter className="h-4 w-4" />Lọc</button>
            <button className="inline-flex h-11 items-center gap-2 rounded-xl border border-slate-200 bg-white px-4" onClick={resetFilter}><RotateCcw className="h-4 w-4" />Đặt lại</button>
            <button className="inline-flex h-11 items-center gap-2 rounded-xl border border-slate-200 bg-white px-4" onClick={exportCsv}><Download className="h-4 w-4" />Xuất CSV</button>
          </div>
        </div>
      </div>
      <div className="card p-4">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-[13px] font-medium text-slate-500">
              <th className="px-3 py-3">Mã ca</th>
              <th className="px-3 py-3">Bệnh nhân / ID</th>
              <th className="px-3 py-3">Thời gian</th>
              <th className="px-3 py-3">Kết quả</th>
              <th className="px-3 py-3">Độ tin cậy</th>
              <th className="px-3 py-3">Trạng thái</th>
              <th className="px-3 py-3">Hành động</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={7} className="py-6 text-center text-slate-500">Đang tải dữ liệu...</td></tr>
            ) : items.length === 0 ? (
              <tr><td colSpan={7} className="py-6 text-center text-slate-500">Không có dữ liệu phù hợp bộ lọc.</td></tr>
            ) : items.map((i) => (
              <tr key={i.id} className="border-t">
                <td className="px-3 py-2 font-semibold">{i.case_code}</td>
                <td className="px-3 py-2">{i.patient_name} / {i.patient_identifier}</td>
                <td className="px-3 py-2">{new Date(i.created_at).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })}</td>
                <td className="px-3 py-2 font-medium">{i.predicted_label || "-"}</td>
                <td className="px-3 py-2 text-blue-600">{i.confidence ? i.confidence.toFixed(2) : "-"}</td>
                <td className="px-3 py-2">{statusBadge(i.status)}</td>
                <td className="px-3 py-2 space-x-3">
                  <button className="inline-flex items-center gap-1 text-blue-600" onClick={() => navigate(`/reports?case_id=${i.id}`)}><Eye className="h-4 w-4" />Xem</button>
                  <button className="inline-flex items-center gap-1 text-slate-600" onClick={exportCsv}><Download className="h-4 w-4" />Tải</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="mt-3 flex items-center justify-between">
          <div className="text-sm text-slate-500">Hiển thị {(page - 1) * 8 + 1} - {Math.min(page * 8, total)} / {total} ca</div>
          <div className="space-x-2"><button className="border px-3 py-1 rounded" onClick={() => setPage(Math.max(1, page - 1))}>{"<"}</button><span>{page}</span><button className="border px-3 py-1 rounded" onClick={() => setPage(page + 1)}>{">"}</button></div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3">
        <div className="card p-4"><div className="text-xs text-slate-500">Tổng số ca</div><div className="mt-1 text-3xl font-bold text-blue-700">{total}</div></div>
        <div className="card p-4"><div className="text-xs text-slate-500">Đã lưu</div><div className="mt-1 text-3xl font-bold text-emerald-600">{quickStat.saved}</div></div>
        <div className="card p-4"><div className="text-xs text-slate-500">Chờ xác nhận</div><div className="mt-1 text-3xl font-bold text-amber-600">{quickStat.pending}</div></div>
        <div className="card p-4"><div className="text-xs text-slate-500">Lỗi</div><div className="mt-1 text-3xl font-bold text-red-600">{quickStat.failed}</div></div>
      </div>

      <div className="card p-4">
        <div className="subtle-title mb-2">Phân bố trạng thái</div>
        <div className="text-sm text-slate-500">Đã lưu: {quickStat.saved} | Chờ xác nhận: {quickStat.pending} | Lỗi: {quickStat.failed}</div>
        </div>
      </div>
  );
}
