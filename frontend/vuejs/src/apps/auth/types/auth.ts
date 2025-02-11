export interface User {
  id: number;
  email: string;
  username: string;
  name?: string;
  balance?: number;
  created_at: string;
  updated_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  isLoggingOut: boolean;
  isLoginPending: boolean;
  initialized: boolean;  // Add this field
}
