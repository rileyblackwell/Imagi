import type { User } from '../types/auth'

export interface AuthResponse {
  token: string;
  user: User;
}

export interface LoginCredentials {
  username: string;  // Changed from email to username
  password: string;
}

export interface UserRegistrationData {
  username: string;
  email: string;
  password: string;
  password_confirmation: string; // Add password confirmation
  terms_accepted: boolean; // Add terms acceptance
}
