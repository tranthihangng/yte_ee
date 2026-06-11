import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ReportResponse } from "@/types/report";
import { assetUrl, formatModuleType } from "@/lib/utils";
import { InfoRow } from "@/components/common/InfoRow";

type ViewerOptions = {
  templateType: string;
  includeImages: boolean;
  includeMetrics: boolean;
  includeNotes: boolean;
  showLogo: boolean;
  maskPersonalInfo: boolean;
};

export function ReportViewer({
  data,
  options,
}: {
  data: ReportResponse;
  options: ViewerOptions;
}) {
  const prediction = data.prediction;
  const caseItem = data.case;
  const artifacts = prediction?.artifacts || {};

  const primaryImage = assetUrl(artifacts.original_image || caseItem.input_file_path);
  const resultImage = assetUrl(
    artifacts.overlay_image || artifacts.gradcam_image || artifacts.detection_image || artifacts.mask_image,
  );

  const patientName = options.maskPersonalInfo ? "******" : caseItem.patient_name;
  const patientId = options.maskPersonalInfo ? "******" : caseItem.patient_identifier;

  return (
    <Card className="print-area">
      <CardHeader className="flex flex-row items-center gap-3 border-b border-slate-200">
        <CardTitle>Xem trước báo cáo</CardTitle>
      </CardHeader>
      <CardContent className="print-page pt-6">
        <div className="rounded-[28px] border border-blue-200 px-8 py-8">
          {options.showLogo && (
            <div className="flex items-center justify-between">
              <div className="text-2xl font-bold text-brand-500">MedAI Assist</div>
              <div className="text-sm text-slate-500">Hệ thống hỗ trợ chẩn đoán bằng AI</div>
            </div>
          )}
          <div className="mt-4 border-b border-brand-500 pb-5 text-center text-[20px] font-bold text-slate-900">
            BÁO CÁO PHÂN TÍCH ẢNH Y TẾ
          </div>

          <div className="mt-6">
            <div className="mb-4 text-[18px] font-semibold text-slate-900">Thông tin ca bệnh</div>
            <div className="grid grid-cols-2 gap-x-10 gap-y-2">
              <InfoRow label="Mã ca" value={caseItem.case_code} />
              <InfoRow label="Bệnh nhân / ID" value={`${patientName} / ${patientId}`} />
              <InfoRow label="Ngày chụp" value={caseItem.study_date} />
              <InfoRow label="Loại phân tích" value={formatModuleType(caseItem.module_type)} />
            </div>
          </div>

          {options.includeImages && (
            <div className="mt-8 grid grid-cols-2 gap-8">
              <div>
                <div className="mb-3 text-center font-semibold">Ảnh gốc</div>
                <div className="flex h-[260px] items-center justify-center rounded-[18px] bg-slate-950 p-3">
                  {primaryImage ? <img src={primaryImage} alt="original" className="max-h-full rounded-xl object-contain" /> : null}
                </div>
              </div>
              <div>
                <div className="mb-3 text-center font-semibold">Ảnh kết quả phân tích</div>
                <div className="flex h-[260px] items-center justify-center rounded-[18px] bg-slate-950 p-3">
                  {resultImage ? <img src={resultImage} alt="result" className="max-h-full rounded-xl object-contain" /> : null}
                </div>
              </div>
            </div>
          )}

          {prediction && options.includeMetrics && (
            <div className="mt-8 rounded-[22px] border border-blue-200 bg-blue-50/40 p-5">
              <div className="mb-4 text-[18px] font-semibold text-slate-900">Kết quả phân tích</div>
              <div className="space-y-2 text-sm">
                <InfoRow label="Phát hiện tổn thương" value={prediction.predicted_label} />
                <InfoRow label="Độ tin cậy mô hình" value={`${(prediction.confidence * 100).toFixed(1)}%`} />
                <InfoRow label="Tóm tắt" value={prediction.summary} />
                {Object.entries(prediction.metrics).map(([key, value]) => (
                  <InfoRow key={key} label={key} value={String(value)} />
                ))}
              </div>
            </div>
          )}

          {options.includeNotes && (
            <div className="mt-8">
              <div className="mb-3 text-[18px] font-semibold text-slate-900">Ghi chú lâm sàng</div>
              <div className="rounded-[18px] bg-slate-50 p-4 text-sm leading-7 text-slate-700">
                {caseItem.notes || "Chưa có ghi chú lâm sàng."}
              </div>
            </div>
          )}

          <div className="mt-10 grid grid-cols-3 border-t border-slate-300 pt-6 text-center text-sm">
            <div>
              <div className="font-semibold">Bác sĩ xác nhận</div>
              <div className="mt-8 font-medium">TS.BS. Phạm Văn Nam</div>
              <div className="text-slate-500">Chuyên khoa Chẩn đoán hình ảnh</div>
            </div>
            <div>
              <div className="font-semibold">Hệ thống AI</div>
              <div className="mt-8 font-medium">MedAI Assist v1.0.0</div>
              <div className="text-slate-500">{formatModuleType(caseItem.module_type)} Model</div>
            </div>
            <div>
              <div className="font-semibold">Ngày tạo báo cáo</div>
              <div className="mt-8 font-medium">{new Date(data.report.created_at).toLocaleString("vi-VN")}</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
