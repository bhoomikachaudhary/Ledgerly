import { api } from "@/lib/api";
import type { TokenPair, User } from "@/types";

export async function signup(data: { email: string; password: string; name: string }) {
  const response = await api.post<User>("/auth/signup", data);
  return response.data;
}

export async function login(data: { email: string; password: string }) {
  const response = await api.post<TokenPair>("/auth/login", data);
  return response.data;
}

export async function getCurrentUser() {
  const response = await api.get<User>("/me");
  return response.data;
}
