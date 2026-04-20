import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";

export function StatusDonutChart({
  saved,
  pending,
  error,
  total,
}: {
  saved: number;
  pending: number;
  error: number;
  total: number;
}) {
  const data = [
    { name: "Đã lưu", value: saved, color: "#2563eb" },
    { name: "Chờ xác nhận", value: pending, color: "#f59e0b" },
    { name: "Lỗi", value: error, color: "#ef4444" },
  ];

  return (
    <div className="flex items-center gap-6">
      <div className="relative h-[170px] w-[170px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} innerRadius={48} outerRadius={72} paddingAngle={2} dataKey="value" stroke="none">
              {data.map((item) => (
                <Cell key={item.name} fill={item.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <div className="text-[18px] font-bold text-slate-900">{total}</div>
          <div className="text-sm text-slate-500">Tổng số ca</div>
        </div>
      </div>
      <div className="space-y-3 text-sm">
        {data.map((item) => (
          <div key={item.name} className="flex items-center gap-3">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
            <span className="text-slate-500">{item.name}</span>
            <span className="ml-auto font-semibold text-slate-900">
              {item.value} ({total ? ((item.value / total) * 100).toFixed(1) : "0"}%)
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
