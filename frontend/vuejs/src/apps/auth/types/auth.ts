// User and Auth State Types
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
  initialized: boolean;
}

// API Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// Service Types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface UserRegistrationData {
  username: string;
  email: string;
  password: string;
  password_confirmation: string;
  terms_accepted: boolean;
}

// Response Types
export interface AuthResponse {
  token: string;
  user: User;
}

export type LoginResponse = ApiResponse<AuthResponse>;
export type RegisterResponse = ApiResponse<AuthResponse>;
