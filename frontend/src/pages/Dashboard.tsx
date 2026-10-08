import { useMemo, useState } from "react";

import { BudgetBar } from "@/components/BudgetBar";
import { CategoryPieChart } from "@/components/CategoryPieChart";
import { EmptyState } from "@/components/EmptyState";
import { Layout } from "@/components/Layout";
import { TrendChart } from "@/components/TrendChart";
import { useCategories } from "@/hooks/useCategories";
import { useSummary, useTrend } from "@/hooks/useBudgets";
import { currentMonth, formatMoney, formatMonthLabel } from "@/lib/format";

export function Dashboard() {
  const [month] = useState(currentMonth());
  const { data: categories } = useCategories();
  const { data: summary, isLoading: summaryLoading } = useSummary(month);
  const { data: trend } = useTrend();

  const colorByCategoryId = useMemo(
    () => Object.fromEntries((categories ?? []).map((c) => [c.id, c.color])),
    [categories]
  );

  const hasSpending = (summary?.categories.length ?? 0) > 0;

  return (
    <Layout>
      <div className="mb-8">
        <p className="text-sm text-ink-soft mb-1">{formatMonthLabel(month)}</p>
        <h2 className="font-display text-4xl amount">
          ₹{summaryLoading ? "—" : formatMoney(summary?.total_spent ?? "0")}
        </h2>
        {summary && parseFloat(summary.total_budget) > 0 && (
          <p className="text-sm text-ink-soft mt-1">
            of <span className="amount">₹{formatMoney(summary.total_budget)}</span> budgeted
          </p>
        )}
      </div>

      {!hasSpending ? (
        <EmptyState
          title="No spending yet this month"
          description="Add your first expense to see it show up here."
        />
      ) : (
        <div className="grid grid-cols-2 gap-10 mb-10">
          <div>
            <h3 className="text-xs uppercase tracking-wide text-ink-soft mb-3">By category</h3>
            <CategoryPieChart categories={summary!.categories} colorByCategoryId={colorByCategoryId} />
          </div>
          <div>
            <h3 className="text-xs uppercase tracking-wide text-ink-soft mb-3">Last 6 months</h3>
            {trend && <TrendChart months={trend.months} />}
          </div>
        </div>
      )}

      {hasSpending && (
        <div>
          <h3 className="text-xs uppercase tracking-wide text-ink-soft mb-1">Budgets</h3>
          <div className="divide-y divide-rule-soft">
            {summary!.categories.map((c) => (
              <BudgetBar
                key={c.category_id}
                categoryName={c.category_name}
                color={colorByCategoryId[c.category_id] ?? "#64748b"}
                spent={c.spent}
                budget={c.budget}
              />
            ))}
          </div>
        </div>
      )}
    </Layout>
  );
}
