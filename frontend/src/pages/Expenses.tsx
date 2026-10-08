import { useState } from "react";

import { EmptyState } from "@/components/EmptyState";
import { ExpenseModal } from "@/components/ExpenseModal";
import { Layout } from "@/components/Layout";
import { useCategories } from "@/hooks/useCategories";
import { useDeleteExpense, useExpenses } from "@/hooks/useExpenses";
import { downloadExportCsv } from "@/lib/endpoints/expenses";
import { formatMoney } from "@/lib/format";
import type { Expense, ExpenseFilters } from "@/types";

const PAGE_SIZE = 20;

export function Expenses() {
  const { data: categories } = useCategories();
  const [filters, setFilters] = useState<ExpenseFilters>({
    sort_by: "spent_on",
    sort_dir: "desc",
    limit: PAGE_SIZE,
    offset: 0,
  });
  const { data, isLoading } = useExpenses(filters);
  const deleteExpense = useDeleteExpense();

  const [modalExpense, setModalExpense] = useState<Expense | "new" | null>(null);

  const categoryName = (id: string) => categories?.find((c) => c.id === id)?.name ?? "—";

  const updateFilter = (patch: Partial<ExpenseFilters>) =>
    setFilters((prev) => ({ ...prev, ...patch, offset: 0 }));

  const goToOffset = (offset: number) => setFilters((prev) => ({ ...prev, offset }));

  const page = Math.floor((filters.offset ?? 0) / PAGE_SIZE);
  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 1;

  return (
    <Layout>
      <div className="flex items-center justify-between mb-6">
        <h2 className="font-display text-2xl">Expenses</h2>
        <div className="flex gap-3">
          <button onClick={() => void downloadExportCsv()} className="btn-secondary">
            Export CSV
          </button>
          <button onClick={() => setModalExpense("new")} className="btn-primary">
            + Add expense
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-3 mb-6 text-sm">
        <select
          className="field-input w-auto"
          value={filters.category_id ?? ""}
          onChange={(e) => updateFilter({ category_id: e.target.value || undefined })}
        >
          <option value="">All categories</option>
          {categories?.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <input
          type="date"
          className="field-input w-auto"
          value={filters.date_from ?? ""}
          onChange={(e) => updateFilter({ date_from: e.target.value || undefined })}
          aria-label="From date"
        />
        <input
          type="date"
          className="field-input w-auto"
          value={filters.date_to ?? ""}
          onChange={(e) => updateFilter({ date_to: e.target.value || undefined })}
          aria-label="To date"
        />
        <select
          className="field-input w-auto"
          value={`${filters.sort_by}:${filters.sort_dir}`}
          onChange={(e) => {
            const [sort_by, sort_dir] = e.target.value.split(":") as [
              ExpenseFilters["sort_by"],
              ExpenseFilters["sort_dir"],
            ];
            updateFilter({ sort_by, sort_dir });
          }}
        >
          <option value="spent_on:desc">Newest first</option>
          <option value="spent_on:asc">Oldest first</option>
          <option value="amount:desc">Amount: high to low</option>
          <option value="amount:asc">Amount: low to high</option>
        </select>
      </div>

      {isLoading ? (
        <p className="text-ink-soft text-sm">Loading…</p>
      ) : !data || data.items.length === 0 ? (
        <EmptyState
          title="No expenses found"
          description="Try different filters, or add your first expense."
          action={
            <button onClick={() => setModalExpense("new")} className="btn-primary">
              + Add expense
            </button>
          }
        />
      ) : (
        <>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-rule text-left text-xs uppercase tracking-wide text-ink-soft">
                <th className="py-2 font-medium">Date</th>
                <th className="py-2 font-medium">Category</th>
                <th className="py-2 font-medium">Note</th>
                <th className="py-2 font-medium text-right">Amount</th>
                <th className="py-2 font-medium text-right"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-rule-soft">
              {data.items.map((expense) => (
                <tr key={expense.id} className="group">
                  <td className="py-2.5 text-ink-soft">{expense.spent_on}</td>
                  <td className="py-2.5">{categoryName(expense.category_id)}</td>
                  <td className="py-2.5 text-ink-soft">{expense.note || "—"}</td>
                  <td className="py-2.5 text-right amount">{formatMoney(expense.amount)}</td>
                  <td className="py-2.5 text-right whitespace-nowrap">
                    <button
                      onClick={() => setModalExpense(expense)}
                      className="text-xs text-ink-soft hover:text-ink mr-3 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => {
                        if (confirm("Delete this expense?")) void deleteExpense.mutateAsync(expense.id);
                      }}
                      className="text-xs text-ink-soft hover:text-brick opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6 text-sm text-ink-soft">
              <span>
                Page {page + 1} of {totalPages} · {data.total} total
              </span>
              <div className="flex gap-2">
                <button
                  disabled={page === 0}
                  onClick={() => goToOffset((page - 1) * PAGE_SIZE)}
                  className="btn-secondary"
                >
                  Previous
                </button>
                <button
                  disabled={page >= totalPages - 1}
                  onClick={() => goToOffset((page + 1) * PAGE_SIZE)}
                  className="btn-secondary"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {modalExpense && categories && (
        <ExpenseModal
          categories={categories}
          expense={modalExpense === "new" ? undefined : modalExpense}
          onClose={() => setModalExpense(null)}
        />
      )}
    </Layout>
  );
}
