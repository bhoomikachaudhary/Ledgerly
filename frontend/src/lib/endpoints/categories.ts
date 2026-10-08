import { api } from "@/lib/api";
import type { Category } from "@/types";

export async function listCategories() {
  const response = await api.get<Category[]>("/categories");
  return response.data;
}

export async function createCategory(data: { name: string; color?: string; icon?: string }) {
  const response = await api.post<Category>("/categories", data);
  return response.data;
}
