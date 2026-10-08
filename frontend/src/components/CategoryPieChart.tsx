import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { formatMoney } from "@/lib/format";
import type { CategorySummary } from "@/types";

interface CategoryPieChartProps {
  categories: CategorySummary[];
  colorByCategoryId: Record<string, string>;
}

export function CategoryPieChart({ categories, colorByCategoryId }: CategoryPieChartProps) {
  const data = categories
    .filter((c) => parseFloat(c.spent) > 0)
    .map((c) => ({ name: c.category_name, value: parseFloat(c.spent), id: c.category_id }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="name" innerRadius={55} outerRadius={85} paddingAngle={2}>
          {data.map((entry) => (
            <Cell key={entry.id} fill={colorByCategoryId[entry.id] ?? "#64748b"} stroke="none" />
          ))}
        </Pie>
        <Tooltip
          formatter={(value: number) => formatMoney(value)}
          contentStyle={{
            border: "1px solid #D9D4C8",
            borderRadius: 0,
            fontSize: 13,
            fontFamily: "Inter, sans-serif",
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
