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

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface AuthResponse {
  token: string;
  user: {
    id: number;
    username: string;
    email: string;
  };
}

export interface UserRegistrationData {
  username: string;
  email: string;
  password: string;
  password_confirmation: string;
  terms_accepted: boolean;
}

export type LoginResponse = ApiResponse<AuthResponse>;
export type RegisterResponse = ApiResponse<AuthResponse>;
