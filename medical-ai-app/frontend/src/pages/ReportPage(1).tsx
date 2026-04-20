import { Download, Mail, Printer } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { toast } from "sonner";
import { LoadingState } from "@/components/common/LoadingState";
import { ReportViewer } from "@/components/report/ReportViewer";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { fetchLatestReportByCase, fetchReportById, generateReport, getDownloadPdfUrl } from "@/services/reportService";
import type { ReportResponse } from "@/types/report";
import { assetUrl } from "@/lib/utils";

export default function ReportPage() {
  const [searchParams] = useSearchParams();
  const reportId = searchParams.get("reportId");
  const caseId = searchParams.get("caseId");
  const [data, setData] = useState<ReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [options, setOptions] = useState({
    templateType: "standard",
    includeImages: true,
    includeMetrics: true,
    includeNotes: true,
    showLogo: true,
    maskPersonalInfo: false,
  });

  const loadData = async () => {
    try {
      setLoading(true);
      let response: ReportResponse;
      if (reportId) response = await fetchReportById(Number(reportId));
      else if (caseId) response = await fetchLatestReportByCase(Number(caseId));
      else throw new Error("Thiếu reportId hoặc caseId");
      setData(response);
      setOptions((prev) => ({
        ...prev,
        templateType: response.report.template_type || prev.templateType,
        includeImages: response.report.include_images,
        includeMetrics: response.report.include_metrics,
        includeNotes: response.report.include_notes,
        maskPersonalInfo: response.report.mask_personal_info,
      }));
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Không tải được báo cáo");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
  }, [reportId, caseId]);

  if (loading) return <LoadingState text="Đang tải báo cáo..." />;
  if (!data) return <div>Không tìm thấy báo cáo.</div>;

  const generateAndReload = async () => {
    try {
      const response = await generateReport(data.case.id, {
        template_type: options.templateType,
        include_images: options.includeImages,
        include_metrics: options.includeMetrics,
        include_notes: options.includeNotes,
        mask_personal_info: options.maskPersonalInfo,
        show_logo: options.showLogo,
      });
      setData(response);
      toast.success("Đã tạo báo cáo PDF mới.");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Không thể tạo PDF");
    }
  };

  const resultImage = assetUrl(
    data.prediction?.artifacts.overlay_image ||
    data.prediction?.artifacts.gradcam_image ||
    data.prediction?.artifacts.detection_image ||
    data.prediction?.artifacts.mask_image,
  );

  return (
    <div className="space-y-6">
      <h1 className="text-[28px] font-bold text-slate-900">Báo cáo ca bệnh</h1>
      <div className="grid grid-cols-[1.48fr_0.92fr] gap-5">
        <ReportViewer data={data} options={options} />

        <div className="space-y-5 report-actions">
          <Card>
            <CardHeader>
              <CardTitle>Tùy chọn báo cáo</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              <div>
                <label className="mb-2 block text-sm text-slate-500">Chọn mẫu báo cáo</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { value: "standard", label: "Chuẩn" },
                    { value: "compact", label: "Rút gọn" },
                    { value: "detailed", label: "Chi tiết" },
                  ].map((item) => (
                    <Button
                      key={item.value}
                      variant={options.templateType === item.value ? "default" : "outline"}
                      onClick={() => setOptions((prev) => ({ ...prev, templateType: item.value }))}
                    >
                      {item.label}
                    </Button>
                  ))}
                </div>
              </div>

              <div>
                <label className="mb-2 block text-sm text-slate-500">Chọn mô-đun hoặc mã ca</label>
                <Select
                  value={String(data.case.id)}
                  onChange={() => undefined}
                  options={[{ value: String(data.case.id), label: `${data.case.case_code} (${data.case.module_type})` }]}
                />
              </div>

              <div className="space-y-3 text-sm">
                {[
                  ["Bao gồm hình ảnh", "includeImages"],
                  ["Bao gồm chỉ số & kết quả", "includeMetrics"],
                  ["Bao gồm ghi chú lâm sàng", "includeNotes"],
                  ["Hiển thị logo MedAI Assist", "showLogo"],
                  ["Làm mờ thông tin cá nhân", "maskPersonalInfo"],
                ].map(([label, key]) => (
                  <div key={key} className="flex items-center gap-3">
                    <Checkbox
                      checked={options[key as keyof typeof options] as boolean}
                      onChange={(checked) => setOptions((prev) => ({ ...prev, [key]: checked }))}
                    />
                    <span>{label}</span>
                  </div>
                ))}
              </div>

              <Button className="w-full" onClick={generateAndReload}>
                Xuất PDF
              </Button>
              <Button className="w-full" variant="outline" onClick={() => window.print()}>
                <Printer className="h-4 w-4" />
                In báo cáo
              </Button>
              <a href={resultImage} target="_blank" rel="noreferrer">
                <Button className="w-full" variant="outline">
                  <Download className="h-4 w-4" />
                  Tải ảnh kết quả
                </Button>
              </a>
              <Button className="w-full" variant="outline" onClick={() => toast.message("API gửi email đã được chuẩn bị ở backend, bạn có thể nối SMTP sau.")}>
                <Mail className="h-4 w-4" />
                Gửi email
              </Button>
              <a href={getDownloadPdfUrl(data.case.id)} target="_blank" rel="noreferrer">
                <Button className="w-full" variant="secondary">Tải PDF đã tạo</Button>
              </a>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Thông tin tạo báo cáo</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-slate-700">
              <div className="flex justify-between"><span className="text-slate-500">Thời gian tạo</span><span>{new Date(data.report.created_at).toLocaleString("vi-VN")}</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Người tạo</span><span>Nguyễn Thị An</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Phiên bản mô hình</span><span>BrainSeg v1.2.0</span></div>
              <div className="flex justify-between"><span className="text-slate-500">Định dạng</span><span>PDF • 1 trang</span></div>
            </CardContent>
          </Card>

          <Card className="bg-blue-50/40">
            <CardHeader>
              <CardTitle>Lưu ý</CardTitle>
            </CardHeader>
            <CardContent className="text-sm leading-7 text-slate-700">
              Báo cáo chỉ mang tính chất tham khảo. Vui lòng kết hợp đánh giá lâm sàng và chỉ định của bác sĩ chuyên khoa.
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
