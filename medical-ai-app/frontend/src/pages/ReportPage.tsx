import { Download, FileDown, Mail, Printer } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useToast } from "../components/common/ToastProvider";
import { reportService } from "../services/reportService";
import { useCaseStore } from "../store/caseStore";

export function ReportPage() {
  const { pushToast } = useToast();
  const [params] = useSearchParams();
  const caseId = Number(params.get("case_id") || useCaseStore.getState().currentCaseId || 0);
  const [templateType, setTemplateType] = useState<"standard" | "compact" | "detail">("standard");
  const [includeImages, setIncludeImages] = useState(true);
  const [includeMetrics, setIncludeMetrics] = useState(true);
  const [includeNotes, setIncludeNotes] = useState(true);
  const [showLogo, setShowLogo] = useState(true);
  const [maskPersonalInfo, setMaskPersonalInfo] = useState(false);
  const [preview, setPreview] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [createdAt, setCreatedAt] = useState("");

  useEffect(() => {
    if (!caseId) return;
    setLoading(true);
    reportService
      .getReportPreview(caseId)
      .then((res) => setPreview(res))
      .catch(() => pushToast("Không tải được dữ liệu ca bệnh", "error"))
      .finally(() => setLoading(false));
  }, [caseId]);

  const maskedPatient = useMemo(() => {
    const patient = preview?.case?.patient_name || "BN-001";
    if (!maskPersonalInfo) return patient;
    return patient.slice(0, 2) + "***";
  }, [preview, maskPersonalInfo]);

  const exportPdf = async () => {
    if (!caseId) return;
    try {
      await reportService.generatePdf(caseId, {
        template_type: templateType,
        include_images: includeImages,
        include_metrics: includeMetrics,
        include_notes: includeNotes,
        mask_personal_info: maskPersonalInfo
      });
      const blob = await reportService.downloadPdf(caseId);
      const url = URL.createObjectURL(new Blob([blob]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `report_${caseId}.pdf`;
      a.click();
      setCreatedAt(new Date().toLocaleString("vi-VN"));
      pushToast("Xuất PDF thành công", "success");
    } catch {
      pushToast("Xuất PDF thất bại", "error");
    }
  };

  return (
    <div className="space-y-5">
      <h1 className="section-title text-[42px]">Báo cáo ca bệnh</h1>
      <div className="grid grid-cols-12 gap-4 items-start">
        <div className="card col-span-8 p-5">
          <div className="mb-4 subtle-title">Xem trước báo cáo</div>
          <div className="rounded-2xl border border-slate-200 bg-white p-6">
            {showLogo && <div className="text-lg font-bold text-blue-700">MedAI Assist</div>}
            <h2 className="mt-2 text-center text-3xl font-bold tracking-tight">BÁO CÁO PHÂN TÍCH ẢNH Y TẾ</h2>
            <div className="mt-5 grid grid-cols-2 gap-4 text-sm">
              <div><span className="text-slate-500">Mã ca:</span> <b>{preview?.case?.case_code || `CA${String(caseId).padStart(5, "0")}`}</b></div>
              <div><span className="text-slate-500">Bệnh nhân / ID:</span> <b>{maskedPatient} / {maskPersonalInfo ? "***" : preview?.case?.patient_identifier || "BN.001"}</b></div>
              <div><span className="text-slate-500">Ngày chụp:</span> <b>{preview?.case?.study_date || "12/06/2025"}</b></div>
              <div><span className="text-slate-500">Loại phân tích:</span> <b>{preview?.case?.module_type || "brain_mri"}</b></div>
            </div>
            {includeImages && <div className="mt-6 grid grid-cols-2 gap-5"><div className="rounded-xl border bg-slate-50 p-3"><div className="mb-2 text-center font-medium">Ảnh gốc</div>{preview?.images?.original_image ? <img className="h-40 w-full rounded-lg bg-black object-contain" src={`http://localhost:8000${preview.images.original_image}`} /> : <div className="h-40 rounded-lg bg-slate-900" />}</div><div className="rounded-xl border bg-slate-50 p-3"><div className="mb-2 text-center font-medium">Ảnh kết quả phân tích</div>{preview?.images?.result_image ? <img className="h-40 w-full rounded-lg bg-black object-contain" src={`http://localhost:8000${preview.images.result_image}`} /> : <div className="h-40 rounded-lg bg-slate-900" />}</div></div>}
            {includeMetrics && <div className="mt-6 rounded-xl border border-blue-100 bg-blue-50 p-4 text-sm"><div className="mb-2 font-semibold">Kết quả phân tích</div><div className="grid grid-cols-2 gap-2 text-slate-700"><div>Phát hiện tổn thương:</div><div>{preview?.prediction?.summary || "-"}</div><div>Nhãn dự đoán:</div><div>{preview?.prediction?.predicted_label || "-"}</div><div>Độ tin cậy:</div><div>{preview?.prediction?.confidence ? Number(preview.prediction.confidence).toFixed(3) : "-"}</div><div>Chỉ số:</div><div>{preview?.prediction?.metrics ? JSON.stringify(preview.prediction.metrics) : "-"}</div></div></div>}
            {includeNotes && <div className="mt-5 rounded-xl border border-slate-200 p-3 text-sm text-slate-600">{preview?.case?.notes || "Chưa có ghi chú lâm sàng."}</div>}
            <div className="mt-6 grid grid-cols-3 text-center text-xs text-slate-600"><div><div className="font-semibold">Bác sĩ xác nhận</div><div className="mt-1">TS.BS. Trần Minh Đức</div></div><div><div className="font-semibold">Hệ thống AI</div><div className="mt-1">MedAI Assist v1.2.0</div></div><div><div className="font-semibold">Ngày tạo báo cáo</div><div className="mt-1">{createdAt || "-"}</div></div></div>
          </div>
        </div>
        <div className="card col-span-4 p-5 no-print">
          <div className="subtle-title">Tùy chọn báo cáo</div>
          <div className="mt-3 grid grid-cols-3 gap-2">
            <button onClick={() => setTemplateType("standard")} className={`rounded-lg py-2 text-sm ${templateType === "standard" ? "bg-blue-600 text-white" : "bg-slate-100"}`}>Chuẩn</button>
            <button onClick={() => setTemplateType("compact")} className={`rounded-lg py-2 text-sm ${templateType === "compact" ? "bg-blue-600 text-white" : "bg-slate-100"}`}>Rút gọn</button>
            <button onClick={() => setTemplateType("detail")} className={`rounded-lg py-2 text-sm ${templateType === "detail" ? "bg-blue-600 text-white" : "bg-slate-100"}`}>Chi tiết</button>
          </div>
          <select className="input-base mt-3">
            <option>{preview?.case?.module_type || "Brain MRI Segmentation"} ({preview?.case?.case_code || "CA00124"})</option>
          </select>
          <div className="space-y-2 mt-3 text-sm">
            <label><input type="checkbox" checked={includeImages} onChange={(e) => setIncludeImages(e.target.checked)} /> Bao gồm hình ảnh</label><br />
            <label><input type="checkbox" checked={includeMetrics} onChange={(e) => setIncludeMetrics(e.target.checked)} /> Bao gồm chỉ số & kết quả</label><br />
            <label><input type="checkbox" checked={includeNotes} onChange={(e) => setIncludeNotes(e.target.checked)} /> Bao gồm ghi chú lâm sàng</label><br />
            <label><input type="checkbox" checked={showLogo} onChange={(e) => setShowLogo(e.target.checked)} /> Hiển thị logo MedAI Assist</label><br />
            <label><input type="checkbox" checked={maskPersonalInfo} onChange={(e) => setMaskPersonalInfo(e.target.checked)} /> Làm mờ thông tin cá nhân</label>
          </div>
          <button className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 py-2 text-white" onClick={exportPdf}><FileDown className="h-4 w-4" />Xuất PDF</button>
          <button className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-xl border py-2" onClick={() => window.print()}><Printer className="h-4 w-4" />In báo cáo</button>
          <button className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-xl border py-2" onClick={() => pushToast("Đã tải ảnh kết quả", "success")}><Download className="h-4 w-4" />Tải ảnh kết quả</button>
          <button className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-xl border py-2" onClick={() => pushToast("Đã gửi email (stub API)", "info")}><Mail className="h-4 w-4" />Gửi email</button>
          <div className="soft-panel mt-3 p-3 text-xs text-slate-600">Thời gian tạo: {createdAt || "-"}<br />Người tạo: Nguyễn Thị An<br />Phiên bản mô hình: BrainSeg v1.2.0<br />Định dạng: PDF (layout gần preview)</div>
        </div>
      </div>
    </div>
  );
}
