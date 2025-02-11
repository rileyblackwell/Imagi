export interface User {
  id: string;
  username: string;  // Add username
  name: string;
  email: string;
  avatar?: string;
  role: 'user' | 'admin';
  createdAt: string;
  balance: number; // Add balance property
}

export interface AuthState {
  user: User | null;
  token: string | null; // Add token
  isAuthenticated: boolean;
  loading: boolean; // Changed from isLoading
  error: string | null;
  isLoggingOut: boolean; // Add isLoggingOut flag
  isLoginPending: boolean; // Add this property
}
