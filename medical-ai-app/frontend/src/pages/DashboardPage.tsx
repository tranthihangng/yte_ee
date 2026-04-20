import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Pie, PieChart, ResponsiveContainer, Cell } from "recharts";
import { Activity, CircleCheck, CircleDashed, CircleX, FlaskConical, Image as ImageIcon, MoveRight } from "lucide-react";
import { dashboardService } from "../services/dashboardService";
import { useToast } from "../components/common/ToastProvider";
import { useAppStore } from "../store/appStore";
import mriCardImage from "../../img/img_mri.png";
import histCardImage from "../../img/img_his.png";
import xrayCardImage from "../../img/img_xray.jpg";

type Summary = { total_cases: number; today_cases: number; avg_accuracy: number; active_modules: number };

export function DashboardPage() {
  const navigate = useNavigate();
  const { pushToast } = useToast();
  const setModule = useAppStore((s) => s.setSelectedModule);
  const [summary, setSummary] = useState<Summary>({ total_cases: 0, today_cases: 0, avg_accuracy: 0, active_modules: 3 });
  const [recent, setRecent] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([dashboardService.getSummary(), dashboardService.getRecentCases()])
      .then(([sum, rec]) => {
        setSummary(sum);
        setRecent(rec);
      })
      .catch(() => {
        setError("Không tải được dữ liệu dashboard");
        pushToast("Lỗi tải dashboard", "error");
      })
      .finally(() => setLoading(false));
  }, []);

  const modules = [
    {
      key: "brain_mri",
      title: "Brain MRI Segmentation",
      desc: "Phân đoạn khối u não trên ảnh MRI",
      badge: "MRI",
      icon: ImageIcon,
      tone: "bg-blue-50 text-blue-600",
      image: mriCardImage
    },
    {
      key: "histopath",
      title: "Histopathology Classification",
      desc: "Phân loại ảnh mô bệnh học",
      badge: "Pathology",
      icon: FlaskConical,
      tone: "bg-violet-50 text-violet-600",
      image: histCardImage
    },
    {
      key: "wrist_xray",
      title: "Wrist X-ray Detection",
      desc: "Phát hiện gãy xương / kim loại",
      badge: "X-ray",
      icon: Activity,
      tone: "bg-emerald-50 text-emerald-600",
      image: xrayCardImage
    }
  ];
  const statusIcon = (status: string) =>
    status.includes("Lỗi") ? <CircleX className="h-4 w-4 text-red-500" /> : status.includes("Chờ") ? <CircleDashed className="h-4 w-4 text-amber-500" /> : <CircleCheck className="h-4 w-4 text-emerald-500" />;

  return (
    <div className="space-y-5">
      <h1 className="text-3xl font-bold">Bảng điều khiển</h1>
      {error && <div className="card border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      <div className="grid grid-cols-4 gap-4">
        {[
          ["Tổng số ca", summary.total_cases],
          ["Ca hôm nay", summary.today_cases],
          ["Độ chính xác TB", `${summary.avg_accuracy}%`],
          ["Mô-đun đang hoạt động", summary.active_modules]
        ].map(([label, value]) => (
          <div key={String(label)} className="card p-4">
            <div className="text-sm text-slate-500">{label}</div>
            <div className="mt-1 text-3xl font-bold text-blue-700">{loading ? "..." : value}</div>
          </div>
        ))}
      </div>
      <div className="card p-4">
        <div className="mb-3 text-xl font-semibold">Chọn mô-đun phân tích</div>
        <div className="grid grid-cols-3 gap-4">
          {modules.map((m) => (
            <div key={m.key} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex gap-3">
                <div className="h-[132px] w-[86px] shrink-0 overflow-hidden rounded-2xl bg-slate-100">
                  <img src={m.image} alt={m.title} className="h-full w-full object-cover" />
                </div>
                <div className="min-w-0 flex-1">
                  <span className="rounded-full bg-blue-100 px-2 py-1 text-xs text-blue-700">{m.badge}</span>
                  <div className="mt-3 flex items-center gap-2 font-semibold">
                    <m.icon className={`h-4 w-4 rounded ${m.tone}`} />
                    <span className="truncate">{m.title}</span>
                  </div>
                  <div className="mt-1 line-clamp-2 text-sm text-slate-500">{m.desc}</div>
                  <button
                    className="mt-4 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-white"
                    onClick={() => {
                      setModule(m.key as any);
                      navigate("/analysis");
                    }}
                  >
                    Phân tích ngay <MoveRight className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div className="card col-span-2 p-4">
          <div className="mb-3 flex justify-between"><div className="font-semibold">Ca gần đây</div><button onClick={() => navigate("/history")} className="text-blue-600">Xem tất cả</button></div>
          <table className="w-full text-sm">
            <thead><tr className="text-left text-slate-500"><th>Mã ca</th><th>Loại ảnh</th><th>Kết quả</th><th>Trạng thái</th></tr></thead>
            <tbody>
              {!loading && recent.length === 0 ? <tr><td colSpan={4} className="py-5 text-center text-slate-500">Chưa có dữ liệu</td></tr> : recent.map((row) => <tr key={row.id} className="border-t"><td className="py-2">{row.case_code}</td><td>{row.module_type}</td><td>{row.predicted_label}</td><td className="inline-flex items-center gap-1 py-2">{statusIcon(row.status)} {row.status}</td></tr>)}
            </tbody>
          </table>
        </div>
        <div className="card p-4">
          <div className="font-semibold">Hiệu suất mô hình</div>
          <div className="h-40">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={[{ name: "ok", value: summary.avg_accuracy }, { name: "rest", value: 100 - summary.avg_accuracy }]} dataKey="value" innerRadius={50} outerRadius={65}>
                  <Cell fill="#2563eb" />
                  <Cell fill="#dbeafe" />
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span>Dice (MRI Segmentation)</span><span>0.891</span></div>
            <div className="flex justify-between"><span>Accuracy (Pathology)</span><span>0.948</span></div>
            <div className="flex justify-between"><span>Confidence (X-ray)</span><span>0.926</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}
