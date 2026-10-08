import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

import type { TokenPair } from "@/types";
import { tokenStorage } from "./tokenStorage";

const API_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000/v1";

export const api = axios.create({ baseURL: API_URL });

api.interceptors.request.use((config) => {
  const token = tokenStorage.getAccess();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// When several requests 401 at once (e.g. a dashboard firing parallel queries),
// only the first should trigger a refresh — the rest wait on the same promise.
let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = tokenStorage.getRefresh();
  if (!refreshToken) return null;

  try {
    const response = await axios.post<TokenPair>(`${API_URL}/auth/refresh`, {
      refresh_token: refreshToken,
    });
    tokenStorage.set(response.data);
    return response.data.access_token;
  } catch {
    tokenStorage.clear();
    return null;
  }
}

interface RetriableConfig extends InternalAxiosRequestConfig {
  _retried?: boolean;
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as RetriableConfig | undefined;

    if (error.response?.status !== 401 || !config || config._retried) {
      if (error.response?.status === 401) {
        tokenStorage.clear();
        window.dispatchEvent(new Event("ledgerly:auth-expired"));
      }
      return Promise.reject(error);
    }

    config._retried = true;
    refreshPromise ??= refreshAccessToken().finally(() => {
      refreshPromise = null;
    });

    const newAccessToken = await refreshPromise;
    if (!newAccessToken) {
      window.dispatchEvent(new Event("ledgerly:auth-expired"));
      return Promise.reject(error);
    }

    config.headers.Authorization = `Bearer ${newAccessToken}`;
    return api(config);
  }
);
