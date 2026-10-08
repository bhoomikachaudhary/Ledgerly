import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis } from "recharts";

import { formatMoney, formatMonthLabel } from "@/lib/format";
import type { TrendPoint } from "@/types";

export function TrendChart({ months }: { months: TrendPoint[] }) {
  const data = months.map((m) => ({
    month: formatMonthLabel(m.month),
    spent: parseFloat(m.total_spent),
  }));

  return (
    <ResponsiveContainer width="100%" height={160}>
      <BarChart data={data} margin={{ top: 4, right: 0, left: 0, bottom: 0 }}>
        <XAxis
          dataKey="month"
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12, fill: "#4A5260", fontFamily: "Inter, sans-serif" }}
        />
        <Tooltip
          cursor={{ fill: "#E8E4D9" }}
          formatter={(value: number) => formatMoney(value)}
          contentStyle={{
            border: "1px solid #D9D4C8",
            borderRadius: 0,
            fontSize: 13,
            fontFamily: "Inter, sans-serif",
          }}
        />
        <Bar dataKey="spent" fill="#2F5233" radius={[2, 2, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
