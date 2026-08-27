"use client";

import { useState, useEffect, useCallback, createContext, useContext } from "react";
import { User, AuthState } from "../types";
import { api } from "../lib/api";

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAdmin: boolean;
  isRiskLead: boolean;
}

export function useAuth(): AuthContextType {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  });

  useEffect(() => {
    const token = localStorage.getItem("fraudguard_token");
    const userStr = localStorage.getItem("fraudguard_user");
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        setAuthState({
          user,
          token,
          isAuthenticated: true,
          isLoading: false,
        });
      } catch {
        setAuthState({ user: null, token: null, isAuthenticated: false, isLoading: false });
      }
    } else {
      setAuthState({ user: null, token: null, isAuthenticated: false, isLoading: false });
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setAuthState((prev) => ({ ...prev, isLoading: true }));
    try {
      const data = await api.login(email, password);
      const user: User = {
        id: data.user_id,
        email: email,
        full_name: data.full_name,
        role: data.role as any,
        is_active: true,
        created_at: new Date().toISOString(),
      };
      localStorage.setItem("fraudguard_token", data.access_token);
      localStorage.setItem("fraudguard_user", JSON.stringify(user));
      setAuthState({
        user,
        token: data.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (err) {
      setAuthState((prev) => ({ ...prev, isLoading: false }));
      throw err;
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("fraudguard_token");
    localStorage.removeItem("fraudguard_user");
    setAuthState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  }, []);

  const isAdmin = authState.user?.role === "ADMIN";
  const isRiskLead = authState.user?.role === "ADMIN" || authState.user?.role === "RISK_LEAD";

  return {
    ...authState,
    login,
    logout,
    isAdmin,
    isRiskLead,
  };
}
