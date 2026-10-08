import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import * as budgetsApi from "@/lib/endpoints/budgets";

export function useBudgets(month: string) {
  return useQuery({
    queryKey: ["budgets", month],
    queryFn: () => budgetsApi.listBudgets(month),
  });
}

export function useSummary(month: string) {
  return useQuery({
    queryKey: ["summary", month],
    queryFn: () => budgetsApi.getSummary(month),
  });
}

export function useTrend() {
  return useQuery({
    queryKey: ["trend"],
    queryFn: budgetsApi.getTrend,
  });
}

export function useUpsertBudget() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: budgetsApi.upsertBudget,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["budgets"] });
      void queryClient.invalidateQueries({ queryKey: ["summary"] });
    },
  });
}
