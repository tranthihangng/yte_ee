import { Lightbulb, UploadCloud, BarChart3 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function UsageTipsCard({ tips }: { tips: string[] }) {
  const icons = [UploadCloud, BarChart3];
  return (
    <Card className="bg-blue-50/50">
      <CardHeader className="flex flex-row items-center gap-3">
        <Lightbulb className="h-5 w-5 text-brand-500" />
        <CardTitle>Gợi ý sử dụng</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {tips.map((tip, index) => {
          const Icon = icons[index] ?? UploadCloud;
          return (
            <div key={tip} className="flex items-start gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-brand-500 shadow-soft">
                <Icon className="h-5 w-5" />
              </div>
              <p className="text-sm leading-7 text-slate-700">{tip}</p>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
