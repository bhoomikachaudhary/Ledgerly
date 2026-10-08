import { formatMoney } from "@/lib/format";

interface BudgetBarProps {
  categoryName: string;
  color: string;
  spent: string;
  budget: string | null;
}

export function BudgetBar({ categoryName, color, spent, budget }: BudgetBarProps) {
  const spentNum = parseFloat(spent);
  const budgetNum = budget ? parseFloat(budget) : null;
  const pct = budgetNum ? Math.min((spentNum / budgetNum) * 100, 100) : 0;

  const barColor = !budgetNum
    ? "bg-ink-soft/40"
    : pct >= 90
      ? "bg-brick"
      : pct >= 75
        ? "bg-amber"
        : "bg-forest";

  return (
    <div className="py-3">
      <div className="flex items-baseline justify-between mb-1.5">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
          <span className="text-sm text-ink">{categoryName}</span>
        </div>
        <span className="amount text-sm">
          {formatMoney(spent)}
          {budget && <span className="text-ink-soft"> / {formatMoney(budget)}</span>}
        </span>
      </div>
      <div className="h-1.5 bg-rule-soft overflow-hidden">
        <div
          className={`h-full transition-all ${barColor}`}
          style={{ width: budgetNum ? `${pct}%` : "0%" }}
        />
      </div>
    </div>
  );
}
