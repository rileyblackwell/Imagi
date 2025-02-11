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
  name: string;
  email: string;
  password: string;
}
