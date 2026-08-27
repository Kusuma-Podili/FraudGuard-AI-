export type UserRole = "ADMIN" | "RISK_LEAD" | "FRAUD_ANALYST" | "AUDITOR";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  department?: string;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
