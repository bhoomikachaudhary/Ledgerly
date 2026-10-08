import { api } from "@/lib/api";
import type { Budget, SummaryResponse, TrendResponse } from "@/types";

export async function listBudgets(month: string) {
  const response = await api.get<Budget[]>("/budgets", { params: { month } });
  return response.data;
}

export async function upsertBudget(data: {
  category_id: string;
  month: string;
  limit_amount: string;
}) {
  const response = await api.put<Budget>("/budgets", data);
  return response.data;
}

export async function getSummary(month: string) {
  const response = await api.get<SummaryResponse>("/summary", { params: { month } });
  return response.data;
}

export async function getTrend() {
  const response = await api.get<TrendResponse>("/summary/trend");
  return response.data;
}
