import { useState } from "react";

import { Layout } from "@/components/Layout";
import { useBudgets, useUpsertBudget } from "@/hooks/useBudgets";
import { useCategories } from "@/hooks/useCategories";
import { currentMonth, formatMonthLabel } from "@/lib/format";

export function Budgets() {
  const [month, setMonth] = useState(currentMonth());
  const { data: categories } = useCategories();
  const { data: budgets } = useBudgets(month);
  const upsertBudget = useUpsertBudget();

  const [drafts, setDrafts] = useState<Record<string, string>>({});

  const budgetFor = (categoryId: string) =>
    drafts[categoryId] ?? budgets?.find((b) => b.category_id === categoryId)?.limit_amount ?? "";

  const save = async (categoryId: string) => {
    const value = drafts[categoryId];
    if (!value || Number.isNaN(parseFloat(value))) return;
    await upsertBudget.mutateAsync({ category_id: categoryId, month, limit_amount: value });
    setDrafts((prev) => {
      const next = { ...prev };
      delete next[categoryId];
      return next;
    });
  };

  return (
    <Layout>
      <div className="flex items-center justify-between mb-6">
        <h2 className="font-display text-2xl">Budgets</h2>
        <input
          type="month"
          className="field-input w-auto"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
        />
      </div>

      <p className="text-sm text-ink-soft mb-6">
        Set a monthly limit per category for {formatMonthLabel(month)}.
      </p>

      <div className="divide-y divide-rule-soft">
        {categories?.map((category) => (
          <div key={category.id} className="flex items-center justify-between py-3">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: category.color }} />
              <span className="text-sm">{category.name}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-ink-soft text-sm">₹</span>
              <input
                type="text"
                inputMode="decimal"
                className="field-input amount w-28 text-right"
                value={budgetFor(category.id)}
                onChange={(e) =>
                  setDrafts((prev) => ({ ...prev, [category.id]: e.target.value }))
                }
                onBlur={() => void save(category.id)}
                placeholder="0.00"
              />
            </div>
          </div>
        ))}
      </div>
    </Layout>
  );
}
