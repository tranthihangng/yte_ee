import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { api } from "@/services/api";
import { LoadingState } from "@/components/common/LoadingState";

type SettingsData = {
  system_name: string;
  theme: string;
  default_confidence_threshold: number;
  output_directory: string;
  brain_mri_model_version: string;
  histopath_model_version: string;
  wrist_xray_model_version: string;
  report_template: string;
  database_url: string;
};

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsData | null>(null);

  useEffect(() => {
    api.get<SettingsData>("/settings").then((response) => setSettings(response.data));
  }, []);

  if (!settings) return <LoadingState text="Đang tải cài đặt..." />;

  const save = async () => {
    try {
      const response = await api.put<SettingsData>("/settings", settings);
      setSettings(response.data);
      toast.success("Đã lưu cài đặt.");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Không lưu được cài đặt");
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-[28px] font-bold text-slate-900">Cài đặt</h1>
      <div className="grid grid-cols-2 gap-5">
        <Card>
          <CardHeader><CardTitle>Hệ thống</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div><label className="mb-2 block text-sm text-slate-500">Tên hệ thống</label><Input value={settings.system_name} onChange={(e) => setSettings({ ...settings, system_name: e.target.value })} /></div>
            <div><label className="mb-2 block text-sm text-slate-500">Theme</label><Select value={settings.theme} onChange={(value) => setSettings({ ...settings, theme: value })} options={[{ value: "light", label: "Light" }, { value: "dark", label: "Dark" }]} /></div>
            <div><label className="mb-2 block text-sm text-slate-500">Ngưỡng mặc định</label><Input type="number" step="0.01" value={settings.default_confidence_threshold} onChange={(e) => setSettings({ ...settings, default_confidence_threshold: Number(e.target.value) })} /></div>
            <div><label className="mb-2 block text-sm text-slate-500">Thư mục output</label><Input value={settings.output_directory} onChange={(e) => setSettings({ ...settings, output_directory: e.target.value })} /></div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Mô hình & báo cáo</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div><label className="mb-2 block text-sm text-slate-500">Brain MRI model version</label><Input value={settings.brain_mri_model_version} onChange={(e) => setSettings({ ...settings, brain_mri_model_version: e.target.value })} /></div>
            <div><label className="mb-2 block text-sm text-slate-500">Histopath model version</label><Input value={settings.histopath_model_version} onChange={(e) => setSettings({ ...settings, histopath_model_version: e.target.value })} /></div>
            <div><label className="mb-2 block text-sm text-slate-500">Wrist X-ray model version</label><Input value={settings.wrist_xray_model_version} onChange={(e) => setSettings({ ...settings, wrist_xray_model_version: e.target.value })} /></div>
            <div><label className="mb-2 block text-sm text-slate-500">Mẫu report mặc định</label><Select value={settings.report_template} onChange={(value) => setSettings({ ...settings, report_template: value })} options={[{ value: "standard", label: "Chuẩn" }, { value: "compact", label: "Rút gọn" }, { value: "detailed", label: "Chi tiết" }]} /></div>
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader><CardTitle>Database</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div><label className="mb-2 block text-sm text-slate-500">Database URL</label><Input value={settings.database_url} onChange={(e) => setSettings({ ...settings, database_url: e.target.value })} /></div>
          <Button onClick={save}>Lưu thay đổi</Button>
        </CardContent>
      </Card>
    </div>
  );
}
