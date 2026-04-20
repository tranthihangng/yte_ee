import { zodResolver } from "@hookform/resolvers/zod";
import { CalendarDays, FileText, RotateCcw, Save, Settings2, Play, ClipboardPen } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { useSearchParams, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { z } from "zod";
import { FileDropzone } from "@/components/analysis/FileDropzone";
import { ImageViewerCard } from "@/components/analysis/ImageViewerCard";
import { PredictionSummaryCard } from "@/components/analysis/PredictionSummaryCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { LoadingState } from "@/components/common/LoadingState";
import { ACCEPT_MAP, MODULE_OPTIONS, assetUrl } from "@/lib/utils";
import { useAppStore } from "@/store/appStore";
import { useCaseStore } from "@/store/caseStore";
import { fetchLatestDraft, saveDraft, uploadCaseFile } from "@/services/caseService";
import { runPrediction } from "@/services/predictionService";

const schema = z.object({
  caseCode: z.string().min(3, "Mã ca tối thiểu 3 ký tự"),
  patientName: z.string().min(1, "Nhập tên hoặc mô tả bệnh nhân"),
  patientIdentifier: z.string().min(1, "Nhập ID bệnh nhân"),
  studyDate: z.string().min(1, "Chọn ngày chụp"),
  moduleType: z.enum(["brain_mri", "histopath", "wrist_xray"]),
  notes: z.string().max(500, "Tối đa 500 ký tự").optional(),
});

type FormValues = z.infer<typeof schema>;

export default function NewAnalysisPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialModule = (searchParams.get("module") as FormValues["moduleType"] | null) ?? "brain_mri";
  const { selectedModule, setSelectedModule } = useAppStore();
  const { currentFile, currentPreview, currentPrediction, setCurrentFile, setCurrentPrediction, clear } = useCaseStore();
  const [loadingDraft, setLoadingDraft] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [confidence, setConfidence] = useState(0.8);
  const [showOverlay, setShowOverlay] = useState(true);
  const [saveToHistory, setSaveToHistory] = useState(true);
  const [exportReport, setExportReport] = useState(true);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      caseCode: `CA${Math.floor(10000 + Math.random() * 89999)}`,
      patientName: "",
      patientIdentifier: "",
      studyDate: new Date().toISOString().slice(0, 10),
      moduleType: initialModule,
      notes: "",
    },
  });

  useEffect(() => {
    setSelectedModule(initialModule);
    form.setValue("moduleType", initialModule);
  }, [initialModule]);

  useEffect(() => {
    fetchLatestDraft()
      .then((draft) => {
        if (draft?.payload) {
          const payload = draft.payload as Record<string, unknown>;
          if (typeof payload.caseCode === "string") form.setValue("caseCode", payload.caseCode);
          if (typeof payload.patientName === "string") form.setValue("patientName", payload.patientName);
          if (typeof payload.patientIdentifier === "string") form.setValue("patientIdentifier", payload.patientIdentifier);
          if (typeof payload.studyDate === "string") form.setValue("studyDate", payload.studyDate);
          if (typeof payload.moduleType === "string") {
            form.setValue("moduleType", payload.moduleType as FormValues["moduleType"]);
            setSelectedModule(payload.moduleType);
          }
          if (typeof payload.notes === "string") form.setValue("notes", payload.notes);
        }
      })
      .finally(() => setLoadingDraft(false));
  }, []);

  const moduleType = form.watch("moduleType");
  const notes = form.watch("notes") || "";

  const accept = useMemo(() => ACCEPT_MAP[moduleType], [moduleType]);

  const onFileChange = async (file: File) => {
    const fileName = file.name.toLowerCase();
    const allowed = accept.split(",").some((suffix) => fileName.endsWith(suffix.trim().toLowerCase()));
    if (!allowed) {
      toast.error(`File không phù hợp với mô-đun ${moduleType}`);
      return;
    }
    const localPreview = URL.createObjectURL(file);
    setCurrentFile(file, localPreview);
    try {
      const upload = await uploadCaseFile(moduleType, file);
      setCurrentFile(file, assetUrl(upload.preview_path));
    } catch {
      // fallback to local preview for image types
    }
  };

  const onSubmit = form.handleSubmit(async (values) => {
    if (!currentFile) {
      toast.error("Vui lòng chọn ảnh trước khi phân tích.");
      return;
    }
    setIsSubmitting(true);
    try {
      const prediction = await runPrediction({
        moduleType: values.moduleType,
        file: currentFile,
        caseCode: values.caseCode,
        patientName: values.patientName,
        patientIdentifier: values.patientIdentifier,
        studyDate: values.studyDate,
        notes: values.notes || "",
        confidenceThreshold: confidence,
        saveToHistory,
        exportReport,
      });
      setCurrentPrediction(prediction);
      toast.success("Phân tích hoàn tất.");
      if (prediction.report_id) {
        toast.success("Báo cáo PDF đã được tạo.");
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Không thể phân tích ảnh");
    } finally {
      setIsSubmitting(false);
    }
  });

  const handleSaveDraft = async () => {
    try {
      const values = form.getValues();
      await saveDraft({
        module_type: values.moduleType,
        payload: {
          ...values,
          confidence,
          showOverlay,
          saveToHistory,
          exportReport,
        },
      });
      toast.success("Đã lưu bản nháp.");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Không thể lưu bản nháp");
    }
  };

  const handleReset = () => {
    clear();
    form.reset({
      caseCode: `CA${Math.floor(10000 + Math.random() * 89999)}`,
      patientName: "",
      patientIdentifier: "",
      studyDate: new Date().toISOString().slice(0, 10),
      moduleType: "brain_mri",
      notes: "",
    });
    setSelectedModule("brain_mri");
    setConfidence(0.8);
    setShowOverlay(true);
    setSaveToHistory(true);
    setExportReport(true);
  };

  if (loadingDraft) return <LoadingState text="Đang tải bản nháp..." />;

  return (
    <div className="space-y-6">
      <h1 className="text-[28px] font-bold text-slate-900">Phân tích mới</h1>
      <div className="grid grid-cols-[0.74fr_1.45fr_0.86fr] gap-5">
        <div className="space-y-5">
          <Card>
            <CardHeader>
              <CardTitle>Thông tin ca bệnh</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="mb-2 block text-sm text-slate-500">Mã ca</label>
                <Input {...form.register("caseCode")} />
                <p className="mt-1 text-xs text-rose-500">{form.formState.errors.caseCode?.message}</p>
              </div>
              <div>
                <label className="mb-2 block text-sm text-slate-500">Họ tên / ID bệnh nhân</label>
                <Input {...form.register("patientName")} placeholder="Nguyễn Văn A - 1985123456" />
                <p className="mt-1 text-xs text-rose-500">{form.formState.errors.patientName?.message}</p>
              </div>
              <div>
                <label className="mb-2 block text-sm text-slate-500">ID bệnh nhân</label>
                <Input {...form.register("patientIdentifier")} placeholder="BN.1987.001" />
                <p className="mt-1 text-xs text-rose-500">{form.formState.errors.patientIdentifier?.message}</p>
              </div>
              <div>
                <label className="mb-2 block text-sm text-slate-500">Ngày chụp</label>
                <Input type="date" {...form.register("studyDate")} />
              </div>
              <div>
                <label className="mb-2 block text-sm text-slate-500">Loại phân tích</label>
                <Select
                  value={moduleType}
                  onChange={(value) => {
                    form.setValue("moduleType", value as FormValues["moduleType"]);
                    setSelectedModule(value);
                  }}
                  options={MODULE_OPTIONS.map((option) => ({ value: option.value, label: option.label }))}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Tải ảnh lên</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <FileDropzone accept={accept} onFileChange={onFileChange} />
              <div>
                <div className="mb-2 text-sm font-medium text-slate-700">Ảnh gốc</div>
                <div className="overflow-hidden rounded-[20px] bg-slate-950 p-3">
                  {currentPreview ? (
                    <img src={currentPreview} alt="preview" className="h-[180px] w-full rounded-[16px] object-contain" />
                  ) : (
                    <div className="flex h-[180px] items-center justify-center text-sm text-slate-400">Chưa có ảnh nào được chọn</div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          <PredictionSummaryCard prediction={currentPrediction} />
        </div>

        <ImageViewerCard preview={currentPreview} artifacts={currentPrediction?.artifacts} moduleType={moduleType} />

        <div className="space-y-5">
          <Card>
            <CardHeader>
              <CardTitle>Thiết lập</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-sm text-slate-600">Ngưỡng tin cậy</span>
                  <span className="rounded-xl bg-blue-50 px-3 py-1 text-sm font-semibold text-brand-500">{confidence.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min={0.5}
                  max={0.95}
                  step={0.01}
                  value={confidence}
                  onChange={(event) => setConfidence(Number(event.target.value))}
                  className="w-full"
                />
                <div className="mt-1 flex justify-between text-sm text-slate-400">
                  <span>0.50</span>
                  <span>0.95</span>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span>Hiển thị lớp phủ</span>
                  <Switch checked={showOverlay} onCheckedChange={setShowOverlay} />
                </div>
                <div className="flex items-center justify-between">
                  <span>Lưu vào lịch sử</span>
                  <Switch checked={saveToHistory} onCheckedChange={setSaveToHistory} />
                </div>
                <div className="flex items-center justify-between">
                  <span>Xuất báo cáo sau phân tích</span>
                  <Switch checked={exportReport} onCheckedChange={setExportReport} />
                </div>
              </div>

              <Button className="w-full" onClick={() => void onSubmit()} disabled={isSubmitting}>
                <Play className="h-4 w-4" />
                {isSubmitting ? "Đang phân tích..." : "Bắt đầu phân tích"}
              </Button>

              <div className="grid grid-cols-2 gap-3">
                <Button variant="secondary" onClick={handleReset}>
                  <RotateCcw className="h-4 w-4" />
                  Đặt lại
                </Button>
                <Button variant="outline" onClick={handleSaveDraft}>
                  <Save className="h-4 w-4" />
                  Lưu bản nháp
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Ghi chú lâm sàng</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea {...form.register("notes")} placeholder="Nhập ghi chú lâm sàng, tiền sử bệnh, triệu chứng..." />
              <div className="mt-2 text-right text-sm text-slate-400">{notes.length}/500</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Hướng dẫn nhanh</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm leading-7 text-slate-700">
              <p>• Chọn đúng loại phân tích để có kết quả chính xác nhất.</p>
              <p>• Ảnh MRI nên rõ nét, không bị nhiễu hoặc cắt mất vùng cần phân tích.</p>
              <p>• Ngưỡng tin cậy cao sẽ cho kết quả ổn định hơn nhưng có thể bỏ sót chi tiết nhỏ.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
