import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import * as expensesApi from "@/lib/endpoints/expenses";
import type { ExpenseFilters } from "@/types";

const EXPENSES_KEY = ["expenses"];
// Summary/trend depend on expense totals, so any expense mutation invalidates them too.
const DEPENDENT_KEYS = [EXPENSES_KEY, ["summary"], ["trend"]];

export function useExpenses(filters: ExpenseFilters) {
  return useQuery({
    queryKey: [...EXPENSES_KEY, filters],
    queryFn: () => expensesApi.listExpenses(filters),
  });
}

function useInvalidateExpenseDependents() {
  const queryClient = useQueryClient();
  return () => DEPENDENT_KEYS.forEach((key) => void queryClient.invalidateQueries({ queryKey: key }));
}

export function useCreateExpense() {
  const invalidate = useInvalidateExpenseDependents();
  return useMutation({
    mutationFn: expensesApi.createExpense,
    onSuccess: invalidate,
  });
}

export function useUpdateExpense() {
  const invalidate = useInvalidateExpenseDependents();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<expensesApi.ExpenseInput> }) =>
      expensesApi.updateExpense(id, data),
    onSuccess: invalidate,
  });
}

export function useDeleteExpense() {
  const invalidate = useInvalidateExpenseDependents();
  return useMutation({
    mutationFn: expensesApi.deleteExpense,
    onSuccess: invalidate,
  });
}

export function useUploadReceipt() {
  const invalidate = useInvalidateExpenseDependents();
  return useMutation({
    mutationFn: ({ id, file }: { id: string; file: File }) => expensesApi.uploadReceipt(id, file),
    onSuccess: invalidate,
  });
}
