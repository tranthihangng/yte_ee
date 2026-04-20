import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricDonutChart } from "@/components/charts/MetricDonutChart";

export function PerformanceCard({
  averageAccuracy,
  performance,
}: {
  averageAccuracy: number;
  performance: { dice: number; accuracy: number; confidence: number };
}) {
  const items = [
    { label: "Dice (MRI Segmentation)", value: performance.dice },
    { label: "Accuracy (Pathology)", value: performance.accuracy },
    { label: "Confidence (X-ray Detection)", value: performance.confidence },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Hiệu suất mô hình</CardTitle>
      </CardHeader>
      <CardContent className="flex items-center gap-8">
        <MetricDonutChart value={averageAccuracy} label="Độ chính xác trung bình" />
        <div className="flex-1 space-y-5">
          {items.map((item) => (
            <div key={item.label}>
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="text-slate-600">{item.label}</span>
                <span className="font-semibold text-slate-900">{item.value.toFixed(3)}</span>
              </div>
              <div className="h-2 rounded-full bg-slate-200">
                <div className="h-2 rounded-full bg-brand-500" style={{ width: `${item.value * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
