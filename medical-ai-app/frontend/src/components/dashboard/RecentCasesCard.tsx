import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { RecentCase } from "@/types/dashboard";
import { formatDateTime, formatModuleType } from "@/lib/utils";
import { StatusBadge } from "@/components/common/StatusBadge";

export function RecentCasesCard({ items }: { items: RecentCase[] }) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Ca gần đây</CardTitle>
        <Link to="/history" className="text-sm font-semibold text-brand-500">
          Xem tất cả
        </Link>
      </CardHeader>
      <CardContent>
        <div className="overflow-hidden rounded-[20px] border border-slate-200">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500">
              <tr>
                <th className="px-4 py-3 font-medium">Mã ca</th>
                <th className="px-4 py-3 font-medium">Loại ảnh</th>
                <th className="px-4 py-3 font-medium">Thời gian</th>
                <th className="px-4 py-3 font-medium">Kết quả</th>
                <th className="px-4 py-3 font-medium">Trạng thái</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-t border-slate-200">
                  <td className="px-4 py-4 font-semibold text-slate-900">{item.case_code}</td>
                  <td className="px-4 py-4">{formatModuleType(item.module_type)}</td>
                  <td className="px-4 py-4">{formatDateTime(item.created_at)}</td>
                  <td className="px-4 py-4 font-medium text-slate-900">{item.predicted_label ?? "--"}</td>
                  <td className="px-4 py-4">
                    <StatusBadge status={item.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
