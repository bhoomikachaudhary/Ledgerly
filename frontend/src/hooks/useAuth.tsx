import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";

import * as authApi from "@/lib/endpoints/auth";
import { tokenStorage } from "@/lib/tokenStorage";
import type { User } from "@/types";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  const loadUser = async () => {
    if (!tokenStorage.getAccess()) {
      setIsLoading(false);
      return;
    }
    try {
      const me = await authApi.getCurrentUser();
      setUser(me);
    } catch {
      tokenStorage.clear();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    void loadUser();

    const handleExpired = () => {
      setUser(null);
      navigate("/login");
    };
    window.addEventListener("ledgerly:auth-expired", handleExpired);
    return () => window.removeEventListener("ledgerly:auth-expired", handleExpired);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = async (email: string, password: string) => {
    const tokens = await authApi.login({ email, password });
    tokenStorage.set(tokens);
    const me = await authApi.getCurrentUser();
    setUser(me);
  };

  const signup = async (email: string, password: string, name: string) => {
    await authApi.signup({ email, password, name });
    await login(email, password);
  };

  const logout = () => {
    tokenStorage.clear();
    setUser(null);
    navigate("/login");
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
