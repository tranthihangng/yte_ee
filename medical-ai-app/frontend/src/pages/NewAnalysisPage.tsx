import { zodResolver } from "@hookform/resolvers/zod";
import { Expand, Hand, Minus, Plus, ScanLine } from "lucide-react";
import { load as loadNpy } from "npyjs";
import { MouseEvent, useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useToast } from "../components/common/ToastProvider";
import { predictionService } from "../services/predictionService";
import { useAppStore } from "../store/appStore";
import { useCaseStore } from "../store/caseStore";

const schema = z.object({
  patient_name: z.string().min(2),
  patient_identifier: z.string().min(2),
  study_date: z.string().min(1),
  notes: z.string().optional()
});
type AnalysisFormValues = z.infer<typeof schema>;

export function NewAnalysisPage() {
  const BACKEND_ASSET_BASE = "http://127.0.0.1:8000";
  const { pushToast } = useToast();
  const selectedModule = useAppStore((s) => s.selectedModule);
  const setSelectedModule = useAppStore((s) => s.setSelectedModule);
  const setCurrentCaseId = useCaseStore((s) => s.setCurrentCaseId);
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const [threshold, setThreshold] = useState(0.8);
  const [saveToHistory, setSaveToHistory] = useState(true);
  const [exportReport, setExportReport] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [npyPreviewUrl, setNpyPreviewUrl] = useState("");
  const [npyPreviewError, setNpyPreviewError] = useState("");
  const { register, handleSubmit, reset, watch } = useForm<AnalysisFormValues>({
    resolver: zodResolver(schema),
    defaultValues: { notes: "" }
  });
  const isNpy = file?.name.toLowerCase().endsWith(".npy") ?? false;
  const originalUrl = useMemo(() => (file && !isNpy ? URL.createObjectURL(file) : ""), [file, isNpy]);
  const acceptedExt = selectedModule === "brain_mri"
    ? ".png,.jpg,.jpeg,.npy,.nii,.nii.gz,.dcm"
    : selectedModule === "histopath" || selectedModule === "tuberculosis_counting"
      ? ".png,.jpg,.jpeg"
      : ".png,.jpg,.jpeg,.dcm";
  const notesValue = watch("notes") || "";

  useEffect(() => {
    let cancelled = false;
    const buildNpyPreview = async () => {
      if (!file || !isNpy) {
        setNpyPreviewUrl("");
        setNpyPreviewError("");
        return;
      }
      try {
        setNpyPreviewError("");
        const parsed = await loadNpy(await file.arrayBuffer());
        const { data, shape } = parsed;
        const values = data as unknown as ArrayLike<number>;
        if (!shape.length) throw new Error("NPY_EMPTY_SHAPE");
        let width = 0;
        let height = 0;
        let voxelAt: (x: number, y: number) => number;
        if (shape.length === 2) {
          height = shape[0];
          width = shape[1];
          voxelAt = (x, y) => Number(values[y * width + x] ?? 0);
        } else if (shape.length === 3) {
          if (shape[0] === 4) {
            height = shape[1];
            width = shape[2];
            voxelAt = (x, y) => Number(values[y * width + x] ?? 0);
          } else if (shape[2] === 4) {
            height = shape[0];
            width = shape[1];
            voxelAt = (x, y) => Number(values[(y * width + x) * 4] ?? 0);
          } else {
            const depth = shape[0];
            const d = Math.floor(depth / 2);
            height = shape[1];
            width = shape[2];
            const sliceOffset = d * height * width;
            voxelAt = (x, y) => Number(values[sliceOffset + y * width + x] ?? 0);
          }
        } else if (shape.length === 4) {
          const depth = shape[1];
          const d = Math.floor(depth / 2);
          height = shape[2];
          width = shape[3];
          const volumeStride = shape[2] * shape[3];
          const sliceOffset = d * volumeStride;
          voxelAt = (x, y) => Number(values[sliceOffset + y * width + x] ?? 0);
        } else {
          throw new Error("NPY_UNSUPPORTED_DIM");
        }
        if (width <= 0 || height <= 0) throw new Error("NPY_INVALID_SHAPE");
        let min = Number.POSITIVE_INFINITY;
        let max = Number.NEGATIVE_INFINITY;
        const gray = new Float32Array(width * height);
        for (let y = 0; y < height; y++) {
          for (let x = 0; x < width; x++) {
            const idx = y * width + x;
            const v = voxelAt(x, y);
            gray[idx] = v;
            if (v < min) min = v;
            if (v > max) max = v;
          }
        }
        const range = max - min || 1;
        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d");
        if (!ctx) throw new Error("CANVAS_CONTEXT_FAILED");
        const imageData = ctx.createImageData(width, height);
        for (let i = 0; i < gray.length; i++) {
          const pixel = Math.max(0, Math.min(255, Math.round(((gray[i] - min) / range) * 255)));
          const base = i * 4;
          imageData.data[base] = pixel;
          imageData.data[base + 1] = pixel;
          imageData.data[base + 2] = pixel;
          imageData.data[base + 3] = 255;
        }
        ctx.putImageData(imageData, 0, 0);
        if (!cancelled) setNpyPreviewUrl(canvas.toDataURL("image/png"));
      } catch {
        if (!cancelled) {
          setNpyPreviewUrl("");
          setNpyPreviewError("Không tạo được preview cho file .npy này");
        }
      }
    };
    buildNpyPreview();
    return () => {
      cancelled = true;
    };
  }, [file, isNpy]);

  const onSubmit = handleSubmit(async (values) => {
    if (!file) {
      pushToast("Vui lòng chọn ảnh đầu vào", "error");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("patient_name", values.patient_name);
      fd.append("patient_identifier", values.patient_identifier);
      fd.append("study_date", values.study_date);
      fd.append("notes", values.notes || "");
      fd.append("confidence_threshold", String(threshold));
      fd.append("save_to_history", String(saveToHistory));
      fd.append("export_report", String(exportReport));
      const endpoint = selectedModule === "brain_mri"
        ? "brain-mri"
        : selectedModule === "histopath"
          ? "histopath"
          : selectedModule === "tuberculosis_counting"
            ? "tuberculosis-counting"
            : "wrist-xray";
      const res = await predictionService.run(endpoint, fd);
      setResult(res);
      if (res.case_id) setCurrentCaseId(res.case_id);
      pushToast("Phân tích hoàn tất", "success");
    } catch {
      setError("Phân tích thất bại hoặc timeout backend.");
      pushToast("Phân tích thất bại", "error");
    } finally {
      setLoading(false);
    }
  });
  const toAssetUrl = (path?: string) => (path ? `${BACKEND_ASSET_BASE}${path}` : "");
  const originalArtifact = result?.artifacts?.original_image;
  const overlayArtifact = result?.artifacts?.overlay_image || result?.artifacts?.gradcam_image || result?.artifacts?.detection_image;
  const mriClassPixels = result?.module === "brain_mri" ? result?.metrics?.class_pixels : null;
  const mriClassLegend = [
    { key: "ncr_net", label: "NCR/NET", colorClass: "bg-red-500" },
    { key: "ed", label: "ED", colorClass: "bg-green-500" },
    { key: "et", label: "ET", colorClass: "bg-yellow-400" }
  ] as const;
  const totalMriTumorPixels = mriClassPixels
    ? Number(mriClassPixels.ncr_net || 0) + Number(mriClassPixels.ed || 0) + Number(mriClassPixels.et || 0)
    : 0;
  // Keep left panel faithful to uploaded original for non-npy files.
  // For npy, there is no browser preview, so use backend-generated original preview.
  const originalPanelImage = !isNpy ? originalUrl : (npyPreviewUrl || (originalArtifact ? toAssetUrl(originalArtifact) : ""));
  const rightPanelImage = toAssetUrl(overlayArtifact) || toAssetUrl(originalArtifact);

  const onMouseMove = (event: MouseEvent<HTMLDivElement>) => {
    if (!dragging) return;
    setOffset((prev) => ({
      x: prev.x + (event.clientX - dragStart.x),
      y: prev.y + (event.clientY - dragStart.y)
    }));
    setDragStart({ x: event.clientX, y: event.clientY });
  };

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Phân tích mới</h1>
      {error && <div className="card border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}
      <div className="grid grid-cols-12 gap-4">
        <div className="card col-span-3 p-4 space-y-3">
          <div className="font-semibold">Thông tin ca bệnh</div>
          <input className="input-base" placeholder="Họ tên / ID bệnh nhân" {...register("patient_name")} />
          <input className="input-base" placeholder="Mã định danh" {...register("patient_identifier")} />
          <input className="input-base" type="date" {...register("study_date")} />
          <select className="input-base" value={selectedModule} onChange={(e) => setSelectedModule(e.target.value as any)}>
            <option value="brain_mri">Brain MRI Segmentation</option>
            <option value="histopath">Histopathology Lung 3-class</option>
            <option value="wrist_xray">Wrist X-ray Detection</option>
            <option value="tuberculosis_counting">Tuberculosis Bacilli Counting</option>
          </select>
          <div className="soft-panel p-3">
            <div className="mb-2 text-sm font-medium">Tải ảnh lên</div>
            <input type="file" accept={acceptedExt} onChange={(e) => setFile(e.target.files?.[0] || null)} />
            <div className="mt-2 text-xs text-slate-500">Định dạng hỗ trợ: {acceptedExt}</div>
            {file && <div className="text-xs mt-2 font-medium">{file.name}</div>}
            {file && !isNpy && <img src={originalUrl} className="mt-2 h-24 w-full rounded-lg border bg-slate-100 object-contain" />}
            {file && isNpy && (
              npyPreviewUrl ? (
                <img src={npyPreviewUrl} className="mt-2 h-24 w-full rounded-lg border bg-slate-100 object-contain" />
              ) : (
                <div className="mt-2 rounded-lg border bg-slate-50 p-2 text-xs text-slate-600">
                  {npyPreviewError || "Đang tạo preview `.npy`..."}
                </div>
              )
            )}
          </div>
        </div>

        <div className="card col-span-6 p-4">
          <div className="font-semibold mb-3">Xem ảnh</div>
          <div className="mb-3 flex gap-2">
            <button className="tab-btn tab-btn-active">Ảnh gốc</button>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-xl border bg-slate-950/90 p-2 text-white">
              {file ? (
                originalPanelImage ? (
                  <img
                    key={`left-${originalPanelImage}`}
                    className="h-[360px] w-full rounded-lg bg-black object-contain"
                    src={originalPanelImage}
                    onError={() => pushToast("Không tải được ảnh gốc từ backend", "error")}
                  />
                ) : (
                  <div className="grid h-[360px] place-items-center text-center text-sm text-slate-200">
                    {npyPreviewError || "Đang tạo preview `.npy`..."}
                  </div>
                )
              ) : (
                "Ảnh gốc"
              )}
            </div>
            <div
              className="relative rounded-xl border bg-slate-950/90 p-2 text-white"
              onMouseDown={(event) => {
                setDragging(true);
                setDragStart({ x: event.clientX, y: event.clientY });
              }}
              onMouseUp={() => setDragging(false)}
              onMouseMove={onMouseMove}
              onMouseLeave={() => setDragging(false)}
            >
              {loading ? (
                <div className="grid h-[360px] place-items-center">Đang phân tích...</div>
              ) : result ? rightPanelImage ? (
                <img
                  key={`right-${rightPanelImage}`}
                  className="h-[360px] w-full rounded-lg bg-black object-contain transition"
                  src={rightPanelImage}
                  onError={() => pushToast("Không tải được ảnh kết quả từ backend", "error")}
                  style={{ transform: `scale(${zoom}) translate(${offset.x / 30}px, ${offset.y / 30}px)` }}
                />
              ) : (
                <div className="grid h-[360px] place-items-center text-center text-sm text-slate-200">Chưa có ảnh cho tab này</div>
              ) : (
                "Kết quả"
              )}
            </div>
          </div>
          {result && (
            <div className="mt-3 rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
              <div className="font-semibold text-slate-800">Thông tin kết quả</div>
              <div className="mt-1 grid grid-cols-2 gap-x-4 gap-y-1">
                <div>Nhãn dự đoán: <b>{result.predicted_label}</b></div>
                <div>Độ tin cậy: <b>{Number(result.confidence).toFixed(3)}</b></div>
                {result.metrics?.dice !== undefined && <div>Dice: <b>{Number(result.metrics.dice).toFixed(3)}</b></div>}
                {result.metrics?.area_cm2 !== undefined && <div>Area: <b>{Number(result.metrics.area_cm2).toFixed(2)} cm2</b></div>}
              </div>
              {mriClassPixels && (
                <div className="mt-3 border-t border-slate-200 pt-2">
                  <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Legend MRI (theo overlay)</div>
                  <div className="space-y-1.5">
                    {mriClassLegend.map((item) => {
                      const px = Number(mriClassPixels[item.key] || 0);
                      const pct = totalMriTumorPixels > 0 ? (px / totalMriTumorPixels) * 100 : 0;
                      return (
                        <div key={item.key} className="flex items-center justify-between rounded-lg bg-white px-2 py-1">
                          <div className="flex items-center gap-2">
                            <span className={`h-3 w-3 rounded-sm ${item.colorClass}`} />
                            <span className="text-xs text-slate-700">{item.label}</span>
                          </div>
                          <div className="text-xs text-slate-600">
                            <b>{pct.toFixed(1)}%</b> ({px}px)
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  <div className="mt-1 text-xs text-slate-500">
                    Tổng pixel vùng u: <b>{totalMriTumorPixels}</b>
                  </div>
                </div>
              )}
            </div>
          )}
          <div className="mt-3 flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 p-2">
            <button className="rounded-lg p-2 hover:bg-slate-200" onClick={() => setZoom((zv) => Math.min(3, zv + 0.1))}><Plus className="h-4 w-4" /></button>
            <button className="rounded-lg p-2 hover:bg-slate-200" onClick={() => setZoom((zv) => Math.max(0.5, zv - 0.1))}><Minus className="h-4 w-4" /></button>
            <button className="rounded-lg p-2 hover:bg-slate-200" onClick={() => setOffset({ x: 0, y: 0 })}><Hand className="h-4 w-4" /></button>
            <input type="range" min={0.5} max={3} step={0.1} value={zoom} onChange={(e) => setZoom(Number(e.target.value))} />
            <button className="rounded-lg p-2 hover:bg-slate-200" onClick={() => { setZoom(1); setOffset({ x: 0, y: 0 }); }}><ScanLine className="h-4 w-4" /></button>
            <button className="rounded-lg p-2 hover:bg-slate-200 ml-auto" onClick={() => document.documentElement.requestFullscreen()}><Expand className="h-4 w-4" /></button>
          </div>
        </div>

        <div className="card col-span-3 p-4 space-y-3">
          <div className="font-semibold">Thiết lập</div>
          <div className="text-sm">Ngưỡng tin cậy: <b>{threshold.toFixed(2)}</b></div>
          <input type="range" min={0.5} max={0.95} step={0.01} value={threshold} onChange={(e) => setThreshold(Number(e.target.value))} />
          <label className="text-sm"><input type="checkbox" checked={saveToHistory} onChange={(e) => setSaveToHistory(e.target.checked)} /> Lưu vào lịch sử</label>
          <label className="text-sm"><input type="checkbox" defaultChecked /> Hiển thị lớp phủ</label>
          <label className="text-sm"><input type="checkbox" checked={exportReport} onChange={(e) => setExportReport(e.target.checked)} /> Xuất báo cáo sau phân tích</label>
          <button className="w-full rounded-xl bg-blue-600 py-2 text-white" disabled={loading} onClick={onSubmit}>{loading ? "Đang chạy..." : "Bắt đầu phân tích"}</button>
          <button className="w-full rounded-xl border py-2" onClick={() => { reset(); setFile(null); setResult(null); setZoom(1); setOffset({ x: 0, y: 0 }); }}>Đặt lại</button>
          <button className="w-full rounded-xl border py-2" onClick={() => pushToast("Đã lưu bản nháp cục bộ", "info")}>Lưu bản nháp</button>
          <div className="soft-panel p-3">
            <div className="mb-1 text-sm font-medium">Ghi chú lâm sàng</div>
            <textarea className="w-full rounded-lg border border-slate-200 p-2 text-sm outline-none focus:border-blue-400" rows={4} maxLength={500} placeholder="Nhập ghi chú lâm sàng, tiền sử, triệu chứng..." {...register("notes")} />
            <div className="mt-1 text-right text-xs text-slate-500">{notesValue.length}/500</div>
          </div>
          <div className="soft-panel p-3 text-sm">
            <div className="font-medium mb-1">Hướng dẫn nhanh</div>
            <ul className="list-disc space-y-1 pl-4 text-slate-600">
              <li>Chọn đúng loại phân tích để có kết quả tốt nhất.</li>
              <li>Ảnh rõ nét giúp ổn định dự đoán của mô hình.</li>
              <li>Ngưỡng cao giúp lọc các vùng có độ tin cậy thấp.</li>
            </ul>
          </div>
        </div>
      </div>
      {result && <div className="card p-4 text-sm"><b>Kết quả:</b> {result.predicted_label} - {Math.round(result.confidence * 100)}%</div>}
    </div>
  );
}
