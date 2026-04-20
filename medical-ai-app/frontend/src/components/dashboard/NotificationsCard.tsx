import { Bell } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function NotificationsCard({
  items,
}: {
  items: Array<{ id: number; title: string; description: string; level: string; created_at: string }>;
}) {
  return (
    <Card className="bg-amber-50/30">
      <CardHeader className="flex flex-row items-center justify-between">
        <div className="flex items-center gap-3">
          <Bell className="h-5 w-5 text-amber-500" />
          <CardTitle>Thông báo hệ thống</CardTitle>
        </div>
        <span className="text-sm font-semibold text-brand-500">Xem tất cả</span>
      </CardHeader>
      <CardContent className="space-y-5">
        {items.map((item) => (
          <div key={item.id} className="flex gap-4">
            <div className={`mt-2 h-2.5 w-2.5 rounded-full ${item.level === "success" ? "bg-emerald-500" : item.level === "warning" ? "bg-amber-500" : "bg-brand-500"}`} />
            <div className="text-sm leading-7 text-slate-700">
              <div className="font-semibold text-slate-900">{item.title}</div>
              <div>{item.description}</div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
