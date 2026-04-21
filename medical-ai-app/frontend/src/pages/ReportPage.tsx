import { Download, FileDown, Mail, Printer, X } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";
import { useSearchParams } from "react-router-dom";
import { useToast } from "../components/common/ToastProvider";
import { reportService } from "../services/reportService";
import { useCaseStore } from "../store/caseStore";
import { fetchBlobByUrl, generateReportPdfBlob, printReportFromElement } from "../utils/reportExport";

type EmailFormState = {
  recipient: string;
  subject: string;
  message: string;
  includePdf: boolean;
  includeOriginalImage: boolean;
  includeResultImage: boolean;
};

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const BACKEND_BASE = "http://localhost:8000";

export function ReportPage() {
  const { pushToast } = useToast();
  const [params] = useSearchParams();
  const caseId = Number(params.get("case_id") || useCaseStore.getState().currentCaseId || 0);
  const reportPreviewRef = useRef<HTMLDivElement | null>(null);
  const [templateType, setTemplateType] = useState<"standard" | "compact" | "detail">("standard");
  const [includeImages, setIncludeImages] = useState(true);
  const [includeMetrics, setIncludeMetrics] = useState(true);
  const [includeNotes, setIncludeNotes] = useState(true);
  const [showLogo, setShowLogo] = useState(true);
  const [maskPersonalInfo, setMaskPersonalInfo] = useState(false);
  const [preview, setPreview] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [sendingEmail, setSendingEmail] = useState(false);
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [createdAt, setCreatedAt] = useState("");
  const [emailForm, setEmailForm] = useState<EmailFormState>({
    recipient: "",
    subject: `Báo cáo ca bệnh CA${String(caseId || 0).padStart(6, "0")}`,
    message: "Xin chào,\nĐây là báo cáo phân tích ảnh y tế từ MedAI Assist.",
    includePdf: true,
    includeOriginalImage: false,
    includeResultImage: true
  });

  useEffect(() => {
    if (!caseId) return;
    setLoading(true);
    reportService
      .getReportPreview(caseId)
      .then((res) => setPreview(res))
      .catch(() => pushToast("Không tải được dữ liệu ca bệnh", "error"))
      .finally(() => setLoading(false));
  }, [caseId, pushToast]);

  const maskedPatient = useMemo(() => {
    const patient = preview?.case?.patient_name || "BN-001";
    if (!maskPersonalInfo) return patient;
    return patient.slice(0, 2) + "***";
  }, [preview, maskPersonalInfo]);

  const caseCode = preview?.case?.case_code || `CA${String(caseId).padStart(6, "0")}`;
  const moduleType = String(preview?.case?.module_type || "report").replace(/[^a-zA-Z0-9_-]/g, "_");
  const originalImageUrl = preview?.images?.original_image ? `${BACKEND_BASE}${preview.images.original_image}` : "";
  const resultImageUrl = preview?.images?.result_image ? `${BACKEND_BASE}${preview.images.result_image}` : "";

  const exportPDF = async () => {
    if (!reportPreviewRef.current || !caseId) return;
    try {
      const blob = await generateReportPdfBlob(reportPreviewRef.current);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `report_${caseCode}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      setCreatedAt(new Date().toLocaleString("vi-VN"));
      pushToast("Đã xuất PDF thành công", "success");
    } catch {
      pushToast("Xuất PDF thất bại", "error");
    }
  };

  const printReport = async () => {
    if (!reportPreviewRef.current) return;
    try {
      await printReportFromElement(reportPreviewRef.current);
    } catch (error: unknown) {
      if (error instanceof Error && error.message === "PRINT_WINDOW_BLOCKED") {
        pushToast("Trình duyệt đang chặn cửa sổ in", "error");
        return;
      }
      pushToast("In báo cáo thất bại", "error");
    }
  };

  const downloadResultImage = async () => {
    if (!resultImageUrl) {
      pushToast("Không tìm thấy ảnh kết quả để tải", "error");
      return;
    }
    const fileName = `${moduleType}_${caseCode}_result.png`;
    try {
      const blob = await fetchBlobByUrl(resultImageUrl);
      const anyWindow = window as Window & {
        showSaveFilePicker?: (options: {
          suggestedName: string;
          types: Array<{ description: string; accept: Record<string, string[]> }>;
        }) => Promise<{ createWritable: () => Promise<{ write: (data: Blob) => Promise<void>; close: () => Promise<void> }> }>;
      };
      if (anyWindow.showSaveFilePicker) {
        const handle = await anyWindow.showSaveFilePicker({
          suggestedName: fileName,
          types: [{ description: "PNG Image", accept: { "image/png": [".png"] } }]
        });
        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();
      } else {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = fileName;
        a.click();
        URL.revokeObjectURL(url);
      }
      pushToast(`Đã tải ảnh kết quả: ${fileName}`, "success");
      pushToast("Hãy kiểm tra thư mục Downloads/Tải xuống của trình duyệt", "info");
    } catch (error: unknown) {
      const message =
        error instanceof Error && error.message.startsWith("FETCH_BLOB_FAILED")
          ? "Ảnh kết quả chưa sẵn sàng, vui lòng thử lại sau"
          : "Tải ảnh kết quả thất bại";
      pushToast(message, "error");
    }
  };

  const validateEmailForm = (): string | null => {
    if (!emailForm.recipient.trim()) return "Thiếu email người nhận";
    if (!EMAIL_REGEX.test(emailForm.recipient.trim())) return "Email người nhận không hợp lệ";
    if (!emailForm.subject.trim()) return "Thiếu tiêu đề email";
    if (!emailForm.includePdf && !emailForm.includeOriginalImage && !emailForm.includeResultImage) {
      return "Vui lòng chọn ít nhất một loại tệp đính kèm";
    }
    return null;
  };

  const prepareEmailAttachments = async (): Promise<Array<{ name: string; blob: Blob; type: string }>> => {
    if (!reportPreviewRef.current) throw new Error("MISSING_PREVIEW");
    const attachments: Array<{ name: string; blob: Blob; type: string }> = [];
    if (emailForm.includePdf) {
      const pdfBlob = await generateReportPdfBlob(reportPreviewRef.current);
      attachments.push({ name: `report_${caseCode}.pdf`, blob: pdfBlob, type: "pdf" });
    }
    if (emailForm.includeOriginalImage) {
      if (!originalImageUrl) throw new Error("NO_ORIGINAL_IMAGE");
      const originalBlob = await fetchBlobByUrl(originalImageUrl);
      attachments.push({ name: `${moduleType}_${caseCode}_original.png`, blob: originalBlob, type: "original_image" });
    }
    if (emailForm.includeResultImage) {
      if (!resultImageUrl) throw new Error("NO_RESULT_IMAGE");
      const resultBlob = await fetchBlobByUrl(resultImageUrl);
      attachments.push({ name: `${moduleType}_${caseCode}_result.png`, blob: resultBlob, type: "result_image" });
    }
    if (!attachments.length) throw new Error("EMPTY_ATTACHMENTS");
    return attachments;
  };

  const sendReportEmail = async () => {
    const validationError = validateEmailForm();
    if (validationError) {
      pushToast(validationError, "error");
      return;
    }
    setSendingEmail(true);
    try {
      const attachments = await prepareEmailAttachments();
      const formData = new FormData();
      formData.append("to_email", emailForm.recipient.trim());
      formData.append("subject", emailForm.subject.trim());
      formData.append("message", emailForm.message.trim());
      formData.append("case_id", String(caseId));
      formData.append("attachment_types", JSON.stringify(attachments.map((item) => item.type)));
      attachments.forEach((item) => formData.append("attachments", item.blob, item.name));
      await reportService.sendReportEmail(formData);
      pushToast(`Đã gửi báo cáo tới ${emailForm.recipient.trim()}`, "success");
      setShowEmailModal(false);
    } catch (error: unknown) {
      const message =
        error instanceof Error
          ? error.message === "EMPTY_ATTACHMENTS"
            ? "Vui lòng chọn ít nhất một loại tệp đính kèm"
            : error.message === "NO_ORIGINAL_IMAGE"
              ? "Không có ảnh gốc để đính kèm"
              : error.message === "NO_RESULT_IMAGE"
                ? "Không có ảnh kết quả để đính kèm"
                : error.message === "MISSING_PREVIEW"
                  ? "Không tìm thấy vùng preview báo cáo"
                  : axios.isAxiosError(error)
                    ? (error.response?.data?.detail || error.message || "Gửi email thất bại do server hoặc timeout")
                    : "Gửi email thất bại do server hoặc timeout"
          : axios.isAxiosError(error)
            ? (error.response?.data?.detail || error.message || "Gửi email thất bại do server hoặc timeout")
            : "Gửi email thất bại do server hoặc timeout";
      pushToast(message, "error");
    } finally {
      setSendingEmail(false);
    }
  };

  return (
    <div className="space-y-5">
      <h1 className="section-title text-[42px]">Báo cáo ca bệnh</h1>
      <div className="grid grid-cols-12 gap-4 items-start">
        <div className="card col-span-8 p-5">
          <div className="mb-4 subtle-title">Xem trước báo cáo</div>
          <div ref={reportPreviewRef} className="print-area rounded-2xl border border-slate-200 bg-white p-6">
            {showLogo && <div className="text-lg font-bold text-blue-700">MedAI Assist</div>}
            <h2 className="mt-2 text-center text-3xl font-bold tracking-tight">BÁO CÁO PHÂN TÍCH ẢNH Y TẾ</h2>
            <div className="mt-5 grid grid-cols-2 gap-4 text-sm">
              <div><span className="text-slate-500">Mã ca:</span> <b>{caseCode}</b></div>
              <div><span className="text-slate-500">Bệnh nhân / ID:</span> <b>{maskedPatient} / {maskPersonalInfo ? "***" : preview?.case?.patient_identifier || "BN.001"}</b></div>
              <div><span className="text-slate-500">Ngày chụp:</span> <b>{preview?.case?.study_date || "12/06/2025"}</b></div>
              <div><span className="text-slate-500">Loại phân tích:</span> <b>{preview?.case?.module_type || "brain_mri"}</b></div>
            </div>
            {includeImages && (
              <div className="mt-6 grid grid-cols-2 gap-5">
                <div className="rounded-xl border bg-slate-50 p-3">
                  <div className="mb-2 text-center font-medium">Ảnh gốc</div>
                  {originalImageUrl ? (
                    <div className="flex min-h-[220px] w-full items-center justify-center rounded-lg bg-slate-100 p-2">
                      <img
                        className="max-h-[220px] max-w-full object-contain object-center"
                        src={originalImageUrl}
                        crossOrigin="anonymous"
                        referrerPolicy="no-referrer"
                      />
                    </div>
                  ) : (
                    <div className="h-[220px] rounded-lg bg-slate-900" />
                  )}
                </div>
                <div className="rounded-xl border bg-slate-50 p-3">
                  <div className="mb-2 text-center font-medium">Ảnh kết quả phân tích</div>
                  {resultImageUrl ? (
                    <div className="flex min-h-[220px] w-full items-center justify-center rounded-lg bg-slate-100 p-2">
                      <img
                        className="max-h-[220px] max-w-full object-contain object-center"
                        src={resultImageUrl}
                        crossOrigin="anonymous"
                        referrerPolicy="no-referrer"
                      />
                    </div>
                  ) : (
                    <div className="h-[220px] rounded-lg bg-slate-900" />
                  )}
                </div>
              </div>
            )}
            {includeMetrics && <div className="mt-6 rounded-xl border border-blue-100 bg-blue-50 p-4 text-sm"><div className="mb-2 font-semibold">Kết quả phân tích</div><div className="grid grid-cols-2 gap-2 text-slate-700"><div>Phát hiện tổn thương:</div><div>{preview?.prediction?.summary || "-"}</div><div>Nhãn dự đoán:</div><div>{preview?.prediction?.predicted_label || "-"}</div><div>Độ tin cậy:</div><div>{preview?.prediction?.confidence ? Number(preview.prediction.confidence).toFixed(3) : "-"}</div><div>Chỉ số:</div><div>{preview?.prediction?.metrics ? JSON.stringify(preview.prediction.metrics) : "-"}</div></div></div>}
            {includeNotes && <div className="mt-5 rounded-xl border border-slate-200 p-3 text-sm text-slate-600">{preview?.case?.notes || "Chưa có ghi chú lâm sàng."}</div>}
            <div className="mt-8 grid grid-cols-3 gap-4 text-center text-xs text-slate-600">
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <div className="font-semibold">Bác sĩ xác nhận</div>
                <div className="mt-1">TS.BS. Phạm Văn Nam</div>
                <div className="mt-5 text-[11px] text-slate-500">Chữ ký bác sỹ / Ký xác nhận</div>
                <div className="mx-auto mt-10 h-px w-10/12 bg-slate-400" />
                <div className="mt-2 text-[10px] text-slate-400">(Ký và ghi rõ họ tên)</div>
              </div>
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <div className="font-semibold">Hệ thống AI</div>
                <div className="mt-1">MedAI Assist v1.2.0</div>
                <div className="mt-12 text-[11px] text-slate-500">Xác nhận kết quả tự động</div>
              </div>
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <div className="font-semibold">Ngày tạo báo cáo</div>
                <div className="mt-1">{createdAt || "-"}</div>
                <div className="mt-12 text-[11px] text-slate-500">Định dạng: A4</div>
              </div>
            </div>
            <div className="h-8" />
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
            <option>{preview?.case?.module_type || "Brain MRI Segmentation"} ({caseCode})</option>
          </select>
          <div className="space-y-2 mt-3 text-sm">
            <label><input type="checkbox" checked={includeImages} onChange={(e) => setIncludeImages(e.target.checked)} /> Bao gồm hình ảnh</label><br />
            <label><input type="checkbox" checked={includeMetrics} onChange={(e) => setIncludeMetrics(e.target.checked)} /> Bao gồm chỉ số & kết quả</label><br />
            <label><input type="checkbox" checked={includeNotes} onChange={(e) => setIncludeNotes(e.target.checked)} /> Bao gồm ghi chú lâm sàng</label><br />
            <label><input type="checkbox" checked={showLogo} onChange={(e) => setShowLogo(e.target.checked)} /> Hiển thị logo MedAI Assist</label><br />
            <label><input type="checkbox" checked={maskPersonalInfo} onChange={(e) => setMaskPersonalInfo(e.target.checked)} /> Làm mờ thông tin cá nhân</label>
          </div>
          <button className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 py-2 text-white" onClick={exportPDF}><FileDown className="h-4 w-4" />Xuất PDF</button>
          <button className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-xl border py-2" onClick={printReport}><Printer className="h-4 w-4" />In báo cáo</button>
          <button className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-xl border py-2" onClick={downloadResultImage}><Download className="h-4 w-4" />Tải ảnh kết quả</button>
          <button className="mt-2 inline-flex w-full items-center justify-center gap-2 rounded-xl border py-2" onClick={() => setShowEmailModal(true)}><Mail className="h-4 w-4" />Gửi email</button>
          <div className="soft-panel mt-3 p-3 text-xs text-slate-600">{loading ? "Đang tải..." : `Thời gian tạo: ${createdAt || "-"}`}<br />Người tạo: Nguyễn Thị An<br />Phiên bản mô hình: BrainSeg v1.2.0<br />Định dạng: PDF (layout gần preview)</div>
        </div>
      </div>
      {showEmailModal && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-900/40 p-4">
          <div className="w-full max-w-xl rounded-2xl bg-white p-5 shadow-xl">
            <div className="mb-4 flex items-center justify-between">
              <div className="text-lg font-semibold">Gửi email báo cáo</div>
              <button className="rounded-lg p-1 hover:bg-slate-100" onClick={() => setShowEmailModal(false)}><X className="h-4 w-4" /></button>
            </div>
            <div className="space-y-3">
              <div>
                <div className="mb-1 text-sm text-slate-600">Email người nhận</div>
                <input className="input-base" value={emailForm.recipient} onChange={(e) => setEmailForm((prev) => ({ ...prev, recipient: e.target.value }))} placeholder="abc@example.com" />
              </div>
              <div>
                <div className="mb-1 text-sm text-slate-600">Tiêu đề</div>
                <input className="input-base" value={emailForm.subject} onChange={(e) => setEmailForm((prev) => ({ ...prev, subject: e.target.value }))} />
              </div>
              <div>
                <div className="mb-1 text-sm text-slate-600">Nội dung ngắn</div>
                <textarea className="w-full rounded-xl border border-slate-200 p-3 text-sm outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100" rows={5} value={emailForm.message} onChange={(e) => setEmailForm((prev) => ({ ...prev, message: e.target.value }))} />
              </div>
              <div>
                <div className="mb-1 text-sm text-slate-600">Tệp đính kèm</div>
                <label className="mb-1 flex items-center gap-2 text-sm"><input type="checkbox" checked={emailForm.includePdf} onChange={(e) => setEmailForm((prev) => ({ ...prev, includePdf: e.target.checked }))} /> Gửi PDF</label>
                <label className="mb-1 flex items-center gap-2 text-sm"><input type="checkbox" checked={emailForm.includeOriginalImage} disabled={!originalImageUrl} onChange={(e) => setEmailForm((prev) => ({ ...prev, includeOriginalImage: e.target.checked }))} /> Gửi ảnh gốc</label>
                <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={emailForm.includeResultImage} disabled={!resultImageUrl} onChange={(e) => setEmailForm((prev) => ({ ...prev, includeResultImage: e.target.checked }))} /> Gửi ảnh kết quả</label>
              </div>
            </div>
            <div className="mt-4 flex justify-end gap-2">
              <button className="rounded-xl border px-4 py-2" onClick={() => setShowEmailModal(false)} disabled={sendingEmail}>Hủy</button>
              <button className="rounded-xl bg-blue-600 px-4 py-2 text-white disabled:opacity-60" onClick={sendReportEmail} disabled={sendingEmail}>{sendingEmail ? "Đang gửi..." : "Gửi email"}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
