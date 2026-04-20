import { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

export function StatCard({
  icon: Icon,
  label,
  value,
  tone,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
  tone: "blue" | "green" | "amber" | "purple";
}) {
  const toneMap = {
    blue: "bg-blue-100 text-blue-600",
    green: "bg-emerald-100 text-emerald-600",
    amber: "bg-amber-100 text-amber-600",
    purple: "bg-violet-100 text-violet-600",
  };

  return (
    <Card className="min-h-[108px]">
      <CardContent className="flex items-center gap-5 pt-6">
        <div className={`flex h-20 w-20 items-center justify-center rounded-[22px] ${toneMap[tone]}`}>
          <Icon className="h-10 w-10" />
        </div>
        <div>
          <div className="text-[15px] text-slate-500">{label}</div>
          <div className="mt-1 text-[22px] font-bold text-slate-900">{value}</div>
        </div>
      </CardContent>
    </Card>
  );
}
