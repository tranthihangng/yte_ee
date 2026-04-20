import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { PredictionResponse } from "@/types/prediction";

export function PredictionSummaryCard({ prediction }: { prediction: PredictionResponse | null }) {
  if (!prediction) return null;

  return (
    <Card className="bg-blue-50/40">
      <CardHeader>
        <CardTitle>Kết quả phân tích</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <div className="flex justify-between gap-3">
          <span className="text-slate-500">Kết luận</span>
          <span className="text-right font-semibold text-slate-900">{prediction.predicted_label}</span>
        </div>
        <div className="flex justify-between gap-3">
          <span className="text-slate-500">Độ tin cậy</span>
          <span className="font-semibold text-emerald-600">{(prediction.confidence * 100).toFixed(1)}%</span>
        </div>
        <div className="rounded-[18px] bg-white p-4 text-slate-700">{prediction.summary}</div>
        <div className="space-y-2">
          {Object.entries(prediction.metrics).map(([key, value]) => (
            <div key={key} className="flex justify-between gap-3">
              <span className="text-slate-500">{key}</span>
              <span className="font-medium text-slate-900">{String(value)}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
