import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";

export function MetricDonutChart({ value, label }: { value: number; label: string }) {
  const chartData = [
    { name: "value", value },
    { name: "rest", value: Math.max(0, 100 - value) },
  ];

  return (
    <div className="relative h-[170px] w-[170px]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={chartData} innerRadius={55} outerRadius={75} dataKey="value" stroke="none">
            <Cell fill="#2563eb" />
            <Cell fill="#e2e8f0" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
        <div className="text-[22px] font-bold text-slate-900">{value.toFixed(1)}%</div>
        <div className="max-w-[90px] text-center text-sm leading-tight text-slate-500">{label}</div>
      </div>
    </div>
  );
}
