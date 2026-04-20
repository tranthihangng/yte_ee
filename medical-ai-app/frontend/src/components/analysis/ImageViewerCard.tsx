import { Expand, Hand, SearchMinus, SearchPlus, ScanSearch } from "lucide-react";
import { useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs } from "@/components/ui/tabs";
import { assetUrl } from "@/lib/utils";

type ViewerProps = {
  preview: string;
  artifacts?: Record<string, string> | null;
  moduleType: string;
};

export function ImageViewerCard({ preview, artifacts, moduleType }: ViewerProps) {
  const [tab, setTab] = useState("original");
  const [zoom, setZoom] = useState(1);

  const rightImage = useMemo(() => {
    if (!artifacts) return "";
    if (tab === "overlay") return assetUrl(artifacts.overlay_image || artifacts.gradcam_image || artifacts.detection_image);
    if (tab === "mask") return assetUrl(artifacts.mask_image || artifacts.gradcam_image || artifacts.detection_image);
    if (tab === "compare") return assetUrl(artifacts.overlay_image || artifacts.gradcam_image || artifacts.detection_image);
    return assetUrl(artifacts.original_image);
  }, [artifacts, tab]);

  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between gap-4">
        <CardTitle>Xem ảnh</CardTitle>
        <Tabs
          tabs={[
            { value: "original", label: "Ảnh gốc" },
            { value: "overlay", label: "Overlay" },
            { value: "mask", label: "Mặt nạ" },
            { value: "compare", label: "So sánh" },
          ]}
          value={tab}
          onChange={setTab}
        />
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="overflow-hidden rounded-[22px] bg-slate-950 p-3">
            <div className="mb-3 text-lg font-semibold text-white">Ảnh gốc</div>
            <div className="flex h-[420px] items-center justify-center overflow-hidden rounded-[18px] bg-black">
              {preview ? (
                <img
                  src={preview}
                  alt="original"
                  style={{ transform: `scale(${zoom})` }}
                  className="max-h-full rounded-[12px] object-contain transition"
                />
              ) : (
                <div className="text-sm text-slate-400">Chưa có ảnh để hiển thị</div>
              )}
            </div>
          </div>
          <div className="overflow-hidden rounded-[22px] bg-slate-950 p-3">
            <div className="mb-3 text-lg font-semibold text-white">
              {moduleType === "brain_mri" ? "Overlay / mặt nạ" : moduleType === "histopath" ? "Grad-CAM" : "Kết quả phát hiện"}
            </div>
            <div className="flex h-[420px] items-center justify-center overflow-hidden rounded-[18px] bg-black">
              {rightImage ? (
                <img
                  src={rightImage}
                  alt="prediction"
                  style={{ transform: `scale(${zoom})` }}
                  className="max-h-full rounded-[12px] object-contain transition"
                />
              ) : (
                <div className="text-sm text-slate-400">Kết quả sẽ hiển thị sau khi phân tích</div>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4 rounded-[20px] bg-slate-50 px-4 py-3">
          <button className="rounded-2xl bg-white p-2 text-slate-600 shadow-soft" onClick={() => setZoom((v) => Math.min(3, v + 0.1))}>
            <SearchPlus className="h-5 w-5" />
          </button>
          <button className="rounded-2xl bg-white p-2 text-slate-600 shadow-soft" onClick={() => setZoom((v) => Math.max(0.5, v - 0.1))}>
            <SearchMinus className="h-5 w-5" />
          </button>
          <button className="rounded-2xl bg-blue-100 p-2 text-brand-600 shadow-soft">
            <Hand className="h-5 w-5" />
          </button>
          <input
            type="range"
            min={0.5}
            max={3}
            step={0.1}
            value={zoom}
            onChange={(event) => setZoom(Number(event.target.value))}
            className="w-[220px]"
          />
          <button className="rounded-2xl bg-white p-2 text-slate-600 shadow-soft" onClick={() => setZoom(1)}>
            <ScanSearch className="h-5 w-5" />
          </button>
          <button className="rounded-2xl bg-white p-2 text-slate-600 shadow-soft" onClick={() => setZoom(1)}>
            <Expand className="h-5 w-5" />
          </button>
        </div>
      </CardContent>
    </Card>
  );
}
