import { ArrowRight, Brain, Microscope, Bone } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const iconMap = {
  brain_mri: Brain,
  histopath: Microscope,
  wrist_xray: Bone,
  tuberculosis_counting: Microscope,
};

const bgMap = {
  brain_mri: "from-slate-900 to-slate-700",
  histopath: "from-fuchsia-200 to-violet-200",
  wrist_xray: "from-slate-800 to-slate-500",
  tuberculosis_counting: "from-rose-300 to-pink-300",
};

export function ModuleCard({
  moduleType,
  badge,
  title,
  description,
}: {
  moduleType: "brain_mri" | "histopath" | "wrist_xray" | "tuberculosis_counting";
  badge: string;
  title: string;
  description: string;
}) {
  const navigate = useNavigate();
  const Icon = iconMap[moduleType];

  return (
    <Card className={`overflow-hidden border ${moduleType === "brain_mri" ? "border-blue-200 bg-blue-50/40" : moduleType === "histopath" ? "border-violet-200 bg-violet-50/40" : moduleType === "wrist_xray" ? "border-emerald-200 bg-emerald-50/40" : "border-rose-200 bg-rose-50/40"}`}>
      <CardContent className="pt-5">
        <div className="mb-4">
          <Badge tone={moduleType === "brain_mri" ? "blue" : moduleType === "histopath" ? "purple" : moduleType === "wrist_xray" ? "green" : "purple"}>{badge}</Badge>
        </div>
        <div className="flex gap-4">
          <div className={`flex h-[145px] w-[118px] shrink-0 items-center justify-center rounded-[22px] bg-gradient-to-br ${bgMap[moduleType]} text-white`}>
            <Icon className="h-12 w-12" />
          </div>
          <div className="flex min-w-0 flex-1 flex-col">
            <div className="text-[18px] font-semibold text-slate-900">{title}</div>
            <div className="mt-2 text-sm leading-6 text-slate-500">{description}</div>
            <Button
              className="mt-auto w-fit rounded-[16px] px-8"
              onClick={() => navigate(`/analysis?module=${moduleType}`)}
            >
              Phân tích ngay
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
