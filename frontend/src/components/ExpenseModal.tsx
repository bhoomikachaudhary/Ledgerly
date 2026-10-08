import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useCreateExpense, useUpdateExpense, useUploadReceipt } from "@/hooks/useExpenses";
import type { Category, Expense } from "@/types";

const schema = z.object({
  category_id: z.string().min(1, "Pick a category"),
  amount: z
    .string()
    .min(1, "Required")
    .refine((v) => !Number.isNaN(parseFloat(v)) && parseFloat(v) > 0, "Must be greater than 0"),
  spent_on: z.string().min(1, "Required"),
  note: z.string().max(500).optional(),
});

type FormValues = z.infer<typeof schema>;

interface ExpenseModalProps {
  categories: Category[];
  expense?: Expense;
  onClose: () => void;
}

export function ExpenseModal({ categories, expense, onClose }: ExpenseModalProps) {
  const isEdit = Boolean(expense);
  const createExpense = useCreateExpense();
  const updateExpense = useUpdateExpense();
  const uploadReceipt = useUploadReceipt();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: expense
      ? {
          category_id: expense.category_id,
          amount: expense.amount,
          spent_on: expense.spent_on,
          note: expense.note ?? "",
        }
      : {
          category_id: categories[0]?.id ?? "",
          amount: "",
          spent_on: new Date().toISOString().slice(0, 10),
          note: "",
        },
  });

  useEffect(() => {
    const onKeydown = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKeydown);
    return () => window.removeEventListener("keydown", onKeydown);
  }, [onClose]);

  const onSubmit = async (values: FormValues) => {
    setError(null);
    try {
      let expenseId = expense?.id;
      if (isEdit && expenseId) {
        await updateExpense.mutateAsync({ id: expenseId, data: values });
      } else {
        const created = await createExpense.mutateAsync(values);
        expenseId = created.id;
      }
      if (pendingFile && expenseId) {
        await uploadReceipt.mutateAsync({ id: expenseId, file: pendingFile });
      }
      onClose();
    } catch {
      setError("Couldn't save this expense. Check the details and try again.");
    }
  };

  return (
    <div className="fixed inset-0 bg-ink/40 flex items-center justify-center z-50 px-4">
      <div className="bg-paper w-full max-w-md border border-rule">
        <div className="px-6 py-5 border-b border-rule">
          <h2 className="font-display text-xl">{isEdit ? "Edit expense" : "Add expense"}</h2>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="px-6 py-5 space-y-4">
          <div>
            <label className="field-label" htmlFor="category_id">
              Category
            </label>
            <select id="category_id" className="field-input" {...register("category_id")}>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
            {errors.category_id && <p className="field-error">{errors.category_id.message}</p>}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="field-label" htmlFor="amount">
                Amount
              </label>
              <input
                id="amount"
                type="text"
                inputMode="decimal"
                placeholder="0.00"
                className="field-input amount"
                {...register("amount")}
              />
              {errors.amount && <p className="field-error">{errors.amount.message}</p>}
            </div>
            <div>
              <label className="field-label" htmlFor="spent_on">
                Date
              </label>
              <input id="spent_on" type="date" className="field-input" {...register("spent_on")} />
              {errors.spent_on && <p className="field-error">{errors.spent_on.message}</p>}
            </div>
          </div>

          <div>
            <label className="field-label" htmlFor="note">
              Note <span className="normal-case text-ink-soft/70">(optional)</span>
            </label>
            <input id="note" type="text" className="field-input" {...register("note")} />
          </div>

          <div>
            <label className="field-label" htmlFor="receipt">
              Receipt <span className="normal-case text-ink-soft/70">(optional)</span>
            </label>
            <input
              id="receipt"
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp,application/pdf"
              onChange={(e) => setPendingFile(e.target.files?.[0] ?? null)}
              className="text-sm text-ink-soft file:mr-3 file:border file:border-rule file:bg-transparent
                file:px-3 file:py-1.5 file:text-xs file:uppercase file:tracking-wide file:text-ink
                hover:file:border-ink file:cursor-pointer"
            />
          </div>

          {error && <p className="field-error">{error}</p>}

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={isSubmitting} className="btn-primary">
              {isSubmitting ? "Saving…" : isEdit ? "Save changes" : "Add expense"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
