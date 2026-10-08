import { api } from "@/lib/api";
import type { Expense, ExpenseFilters, ExpenseListResponse } from "@/types";

export async function listExpenses(filters: ExpenseFilters = {}) {
  const response = await api.get<ExpenseListResponse>("/expenses", { params: filters });
  return response.data;
}

export interface ExpenseInput {
  category_id: string;
  amount: string;
  spent_on: string;
  note?: string;
}

export async function createExpense(data: ExpenseInput) {
  const response = await api.post<Expense>("/expenses", data);
  return response.data;
}

export async function updateExpense(id: string, data: Partial<ExpenseInput>) {
  const response = await api.patch<Expense>(`/expenses/${id}`, data);
  return response.data;
}

export async function deleteExpense(id: string) {
  await api.delete(`/expenses/${id}`);
}

export async function uploadReceipt(id: string, file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post<Expense>(`/expenses/${id}/receipt`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function downloadExportCsv() {
  // The export endpoint requires auth, so this goes through the api client
  // (with its Bearer header) rather than a plain <a href> link.
  const response = await api.get("/expenses/export", { responseType: "blob" });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.download = "expenses.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
