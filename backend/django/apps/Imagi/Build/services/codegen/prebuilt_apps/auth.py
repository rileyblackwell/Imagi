"""
Auth app prebuilt template.

The generated files are verbatim copies of Imagi's own auth module — the
Django `apps/Auth` API (register/signin/logout/init/user) and the Vue
`src/apps/auth` app (services, stores, views, components) — so generated
projects get exactly the auth code Imagi itself runs.

The only deliberate deviations from the Imagi source are the ones a
generated project needs:
  * `apps.py` declares `label = 'user_auth'` (the generated app lives at
    `apps.auth`, whose default label collides with `django.contrib.auth`;
    Imagi avoids this by using the capitalized `apps.Auth` path).
  * The backend test module imports from `apps.auth` instead of `apps.Auth`.
  * `AuthLayout.vue` drops Imagi's `DefaultLayout`/`ImagiLogo` shared
    components (which don't exist in generated projects) in favor of a
    self-contained layout with a plain text brand link, and uses a
    `prefers-color-scheme` media query instead of Imagi's `:root.dark`
    class strategy.
  * `AuthLinks.vue` / `AuthHeader.vue` swap the "Imagi" brand copy for a
    neutral "App" equivalent.

The frontend files rely on the project scaffold that ProjectCreationService
always writes: `@/shared/services/api` (axios client with token + CSRF
interceptors) and `@/shared/stores/auth` (global auth store).
"""
from __future__ import annotations

from typing import Dict, List


def auth_app_files() -> List[Dict[str, str]]:
    """Generate the auth app files (frontend + backend) for a new project."""
    files: List[Dict[str, str]] = []

    # ========== Frontend Files ==========

    # Main index.ts — verbatim from Imagi src/apps/auth/index.ts
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/index.ts',
        'type': 'typescript',
        'content': '''export { useAuth } from './composables/useAuth'
export { useAuthStore } from './stores/index'
export type { User, AuthState } from './types/auth'
'''
    })

    # ===== Types — verbatim from Imagi src/apps/auth/types/ =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/types/auth.ts',
        'type': 'typescript',
        'content': '''// User and Auth State Types
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
'''
    })

    files.append({
        'name': 'frontend/vuejs/src/apps/auth/types/form.ts',
        'type': 'typescript',
        'content': '''export interface RegisterFormValues {
  username?: string;
  email?: string;
  password?: string;
  agreeToTerms?: boolean;
  [key: string]: unknown;
}

export interface PasswordRequirementsRef {
  isValid: boolean;
}

export interface LoginFormValues {
  username?: string;
  password?: string;
  [key: string]: unknown;
}
'''
    })

    # ===== Validation Plugin — verbatim from Imagi src/apps/auth/plugins/validation.ts =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/plugins/validation.ts',
        'type': 'typescript',
        'content': '''import { configure, defineRule } from 'vee-validate'
import { required, email } from '@vee-validate/rules'
import { localize } from '@vee-validate/i18n'
import type { App } from 'vue'

// Define base rules
defineRule('required', () => true)
defineRule('email', (value: string) => {
  if (value && !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(value)) {
    return 'Please enter a valid email address'
  }
  return true
})

// Username validation - must be at least 3 characters, alphanumeric with underscores allowed
defineRule('username', (value: string) => {
  if (!value) return true // Let required rule handle empty values
  if (value.length < 3) return 'Username must be at least 3 characters'
  if (value.length > 150) return 'Username must be less than 150 characters'
  if (!/^[a-zA-Z0-9_]+$/.test(value)) return 'Username can only contain letters, numbers, and underscores'
  return true
})

// Add terms agreement validation
defineRule('terms', () => true)

// Registration specific password validation
defineRule('registration_password', (value: string) => {
  if (value && value.length < 8) return 'Password must be at least 8 characters'
  if (value && !/[A-Z]/.test(value)) return 'Password must contain at least one uppercase letter'
  if (value && !/[a-z]/.test(value)) return 'Password must contain at least one lowercase letter'
  if (value && !/[0-9]/.test(value)) return 'Password must contain at least one number'
  return true
})

defineRule('password_confirmation', (value: string, [target]: string[]) => {
  if (value && target && value !== target) {
    return 'Passwords must match'
  }
  return true
})

// Add login-specific validation rules
defineRule('login_username', () => true)

defineRule('login_password', () => true)

// Expand error messages to include login-specific messages
const errorMessages = {
  // Registration errors
  'This username is already taken. Please choose another one.': 'This username is already taken. Please try another one.',
  'A user is already registered with this e-mail address.': 'This email is already registered. Please use another one or sign in.',
  'Password must be at least 8 characters long': 'Password must be at least 8 characters long.',
  'Passwords don\\'t match': 'Passwords don\\'t match. Please make sure they are identical.',
  'Unable to complete registration. Please try again.': 'Unable to complete registration. Please try again.',
  'Registration failed': 'Registration failed due to a backend error. Please try again.',

  // Login errors
  'No account found with this username': 'No account found with this username. Please check your spelling or create an account.',
  'Invalid password. Please try again': 'Incorrect password. Please try again.',
  'This account has been disabled': 'This account has been disabled. Please contact support.',
  'Unable to log in with provided credentials.': 'Invalid username or password. Please try again.',
  'Invalid login credentials': 'Invalid username or password. Please try again.',
  'Username is required': 'Username is required.',
  'Password is required': 'Password is required.',
  'Not found.': 'Account not found. Please check your username.',
  'Authentication credentials were not provided.': 'Please enter your login credentials.',
  'Invalid credentials': 'Username or password is incorrect.',
  'Login failed. Please try again later': 'Login failed. Please try again later.',
  'Login failed: No token received': 'Unable to log in. Please try again.',
  'Network Error': 'Unable to connect to server. Please check your internet connection.',
  'Network Error: Unable to connect to server': 'Unable to reach the backend server. Please check your connection.',
  'Login failed: Please try again': 'Login failed. Please try again later.',
  'Login failed: Invalid response format': 'Unable to complete login. Please try again.',
  'Invalid server response: Missing token': 'Unable to complete login. Please try again.',
  'Login failed': 'Login failed due to a backend error. Please try again.',
  'default': 'An unexpected error occurred. Please try again.'
} as const

export const formatAuthError = (error: unknown, context: 'login' | 'register' = 'login'): string => {
  if (!error) return errorMessages.default

  if (error instanceof Error) {
    const message = error.message

    // Check if this is an axios error with a response
    const axiosError = error as any
    if (axiosError?.response?.data) {
      const responseData = axiosError.response.data
      const status = axiosError.response.status

      if (status >= 500) {
        return 'Backend server error. Please try again later.'
      }

      // Check for different error formats
      if (responseData.error) {
        return errorMessages[responseData.error as keyof typeof errorMessages] || responseData.error
      }

      if (responseData.detail) {
        if (typeof responseData.detail === 'object') {
          // Convert detailed validation errors to readable messages
          const fieldMessages = []

          for (const [field, message] of Object.entries(responseData.detail)) {
            const normalizedMessage = Array.isArray(message) ? message[0] : message
            if (field === 'non_field_errors' || field === 'error') {
              fieldMessages.push(normalizedMessage)
            } else {
              const fieldLabel = field.replace(/_/g, ' ')
              if (field === 'password') {
                fieldMessages.push(`Password: ${normalizedMessage}`)
              } else if (field === 'username') {
                fieldMessages.push(`Username: ${normalizedMessage}`)
              } else if (field === 'email') {
                fieldMessages.push(`Email: ${normalizedMessage}`)
              } else {
                fieldMessages.push(`${fieldLabel}: ${normalizedMessage}`)
              }
            }
          }

          return fieldMessages.join('\\n')
        }

        return responseData.detail
      }

      // Handle non_field_errors array
      if (responseData.non_field_errors && Array.isArray(responseData.non_field_errors)) {
        return responseData.non_field_errors[0]
      }
    }

    // Check message against our known error messages
    const formattedMessage = errorMessages[message as keyof typeof errorMessages]
    return formattedMessage || message
  }

  // If error is just a string
  if (typeof error === 'string') {
    return errorMessages[error as keyof typeof errorMessages] || error
  }

  return errorMessages.default
}

export const validationPlugin = {
  install: (app: App) => {
    configure({
      validateOnInput: false,
      validateOnBlur: false,
      validateOnChange: false,
      validateOnModelUpdate: false,
      generateMessage: () => '',
    })
  }
}

export { defineRule, errorMessages }
'''
    })

    # ===== API Service — verbatim from Imagi src/apps/auth/services/api.ts =====
    # Uses the shared axios client written by the project scaffold.
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/services/api.ts',
        'type': 'typescript',
        'content': '''import api from '@/shared/services/api'
import type {
  User,
  LoginCredentials,
  AuthResponse,
  UserRegistrationData
} from '@/apps/auth/types/auth'

// API Configuration
const API_PATH = '/v1/auth'

// Helper function to get CSRF token from cookies
function getCookie(name: string): string | null {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (const rawCookie of cookies) {
      const cookie = rawCookie.trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

let logoutPromise: Promise<any> | null = null

export const AuthAPI = {
  formatFieldErrors(detail: Record<string, unknown>): string {
    const fieldMessages: string[] = []
    for (const [field, message] of Object.entries(detail)) {
      const normalizedMessage = Array.isArray(message) ? message[0] : message
      if (field === 'non_field_errors' || field === 'error') {
        fieldMessages.push(String(normalizedMessage))
      } else if (field === 'username') {
        fieldMessages.push(`Username: ${normalizedMessage}`)
      } else if (field === 'password') {
        fieldMessages.push(`Password: ${normalizedMessage}`)
      } else if (field === 'email') {
        fieldMessages.push(`Email: ${normalizedMessage}`)
      } else {
        fieldMessages.push(`${field.replace(/_/g, ' ')}: ${normalizedMessage}`)
      }
    }
    return fieldMessages.join('\\n')
  },
  async getCSRFToken() {
    try {
      const response = await api.get(`${API_PATH}/csrf/`, {
        timeout: 30000,
        headers: {
          'X-Request-Type': 'csrf-token',
          'X-Frontend-Service': 'vue-frontend'
        }
      })
      return response
    } catch (error: any) {
      throw error
    }
  },

  async ensureCSRFToken(): Promise<string | null> {
    let csrfToken = getCookie('csrftoken')

    if (!csrfToken) {
      try {
        await this.getCSRFToken()
        csrfToken = getCookie('csrftoken')

        if (!csrfToken) {
          throw new Error('Failed to obtain CSRF token')
        }
      } catch (error: any) {
        throw error
      }
    }

    return csrfToken
  },

  async init(): Promise<{ data: { isAuthenticated: boolean; user: User } }> {
    return await api.get(`${API_PATH}/init/`)
  },

  async login(credentials: LoginCredentials): Promise<{ data: AuthResponse }> {
    try {
      if (!credentials?.username || !credentials?.password) {
        throw new Error('Username and password are required')
      }

      const csrfToken = await this.ensureCSRFToken();
      if (!csrfToken) {
        throw new Error('Authentication error: Could not obtain security token');
      }

      const response = await api.post(`${API_PATH}/signin/`, credentials, {
        headers: csrfToken !== 'bypass' ? { 'X-CSRFToken': csrfToken } : {},
        timeout: 15000
      });

      if (!response.data) {
        throw new Error('Invalid server response: Empty response')
      }

      if (!response.data.token && !response.data.key) {
        throw new Error('Invalid server response: Missing token')
      }

      return {
        data: {
          token: response.data.token || response.data.key,
          user: response.data.user || {}
        }
      }
    } catch (error: any) {
      if (error.response?.status === 400) {
        const errorData = error.response.data
        if (errorData?.detail && typeof errorData.detail === 'object') {
          throw new Error(this.formatFieldErrors(errorData.detail))
        }
        const errorMessage = errorData?.non_field_errors?.[0] ||
                           errorData?.detail ||
                           errorData?.error ||
                           'Invalid username or password'
        throw new Error(errorMessage)
      } else if (error.response?.status === 401) {
        throw new Error('Invalid username or password')
      } else if (error.response?.status === 429) {
        throw new Error('Too many login attempts. Please try again later.')
      } else if (error.response?.status >= 500) {
        throw new Error('Backend server error. Please try again later.')
      } else if (!error.response) {
        throw new Error('Network Error: Unable to connect to server')
      }

      throw error
    }
  },

  async register(userData: UserRegistrationData): Promise<{ data: AuthResponse }> {
    try {
      const csrfToken = await this.ensureCSRFToken()
      if (!csrfToken) {
        throw new Error('Registration error: Could not obtain security token')
      }

      if (!userData.username || userData.username.trim() === '') {
        throw new Error('Username is required')
      }

      if (!userData.password || userData.password.length < 8) {
        throw new Error('Password must be at least 8 characters long')
      }

      if (userData.password !== userData.password_confirmation) {
        throw new Error('Passwords do not match')
      }

      const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/
      if (!userData.email || !emailRegex.test(userData.email)) {
        throw new Error('Please enter a valid email address')
      }

      const fullRequestUrl = `${API_PATH}/register/`;

      const headers: Record<string, string> = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      };

      if (csrfToken && csrfToken !== 'bypass') {
        headers['X-CSRFToken'] = csrfToken;
      }

      // Only send fields that backend expects
      const registrationData = {
        username: userData.username,
        email: userData.email,
        password: userData.password,
        password_confirmation: userData.password_confirmation
      }

      const response = await api.post(fullRequestUrl, registrationData, {
        headers,
        timeout: 15000
      })

      return {
        data: {
          token: response.data.token || response.data.key,
          user: response.data.user || {}
        }
      }
    } catch (error: any) {
      // Handle validation errors from server
      if (error.response?.status === 400) {
        const errorData = error.response.data

        // Handle field-specific errors
        if (errorData.username) {
          const usernameError = Array.isArray(errorData.username) ? errorData.username[0] : errorData.username
          throw new Error(`Username: ${usernameError}`)
        }
        if (errorData.email) {
          const emailError = Array.isArray(errorData.email) ? errorData.email[0] : errorData.email
          throw new Error(`Email: ${emailError}`)
        }
        if (errorData.password) {
          const passwordError = Array.isArray(errorData.password) ? errorData.password[0] : errorData.password
          throw new Error(`Password: ${passwordError}`)
        }
        if (errorData.password_confirmation) {
          const confirmError = Array.isArray(errorData.password_confirmation) ? errorData.password_confirmation[0] : errorData.password_confirmation
          throw new Error(`${confirmError}`)
        }
        if (errorData.non_field_errors) {
          const nonFieldError = Array.isArray(errorData.non_field_errors) ? errorData.non_field_errors[0] : errorData.non_field_errors
          throw new Error(nonFieldError)
        }
        if (errorData.error) {
          throw new Error(errorData.error)
        }
        if (errorData.detail) {
          const detail = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail)
          throw new Error(detail)
        }

        // If we have any error data, show it
        const firstKey = Object.keys(errorData)[0]
        if (firstKey) {
          const firstError = errorData[firstKey]
          const errorMsg = Array.isArray(firstError) ? firstError[0] : firstError
          throw new Error(`${firstKey}: ${errorMsg}`)
        }

        // Generic validation error
        throw new Error('Registration failed. Please check your input and try again.')
      }

      // Handle other HTTP errors
      if (error.response?.status === 409) {
        throw new Error('An account with this email or username already exists')
      }

      if (error.response?.status === 429) {
        throw new Error('Too many registration attempts. Please try again later.')
      }

      if (error.response?.status >= 500) {
        throw new Error('Backend server error. Please try again later.')
      }

      // Handle network errors
      if (!error.response) {
        throw new Error('Network Error: Unable to connect to server')
      }

      // Re-throw other errors
      throw error
    }
  },

  async logout(): Promise<void> {
    if (logoutPromise) {
      return logoutPromise
    }

    try {
      logoutPromise = api.post(`${API_PATH}/logout/`, {})
      await logoutPromise

      localStorage.removeItem('token')
      // The shared API client will handle removing the Authorization header
    } catch (error) {
      throw error
    } finally {
      logoutPromise = null
    }
  },

  async updateUser(userData: Partial<User>): Promise<{ data: User }> {
    const response = await api.patch(`${API_PATH}/user/`, userData)
    return response
  }
}
'''
    })

    # ===== Auth Module Store — verbatim from Imagi src/apps/auth/stores/index.ts =====
    # Delegates global state to the shared auth store written by the scaffold.
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/stores/index.ts',
        'type': 'typescript',
        'content': '''import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { AuthAPI } from '../services/api'
import { useAuthStore as useGlobalAuthStore } from '@/shared/stores/auth'
import type { LoginCredentials, AuthResponse, UserRegistrationData, User } from '../types/auth'

/**
 * Auth module store for handling authentication-specific processes
 * This store manages local auth state for login, logout, and registration
 * while delegating global state management to the root auth store
 */
export const useAuthStore = defineStore('auth-module', () => {
  // Local state for authentication processes
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isLoggingOut = ref(false)
  const lastAuthAction = ref<string | null>(null)

  // Get global auth store
  const globalAuthStore = useGlobalAuthStore()

  // Computed properties
  const isAuthenticated = computed(() => globalAuthStore.isAuthenticated)
  const user = computed(() => globalAuthStore.user)
  const initialized = computed(() => globalAuthStore.initialized)

  // Actions
  /**
   * Login user with credentials
   * Handles local loading/error state and delegates to global auth store on success
   */
  const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
    try {
      loading.value = true
      error.value = null
      lastAuthAction.value = 'login'

      const response = await AuthAPI.login(credentials)

      // Handle successful login using global auth store
      if (response?.data?.token) {
        // Update global auth state
        globalAuthStore.setAuthState(response.data.user, response.data.token)
        return response.data
      }

      throw new Error('Invalid response from server')
    } catch (err: any) {
      const errorMessage = err.message || 'Login failed'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Register new user
   * Handles local loading/error state and delegates to global auth store on success
   */
  const register = async (userData: UserRegistrationData): Promise<AuthResponse> => {
    try {
      loading.value = true
      error.value = null
      lastAuthAction.value = 'register'

      const response = await AuthAPI.register(userData)

      // Handle successful registration using global auth store
      if (response?.data?.token) {
        // Update global auth state
        globalAuthStore.setAuthState(response.data.user, response.data.token)
        return response.data
      }

      throw new Error('Invalid response from server')
    } catch (err: any) {
      const errorMessage = err.message || 'Registration failed'
      error.value = errorMessage
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Logout user
   * Handles local loading state and delegates to global auth store
   * @param {import('vue-router').Router} [router] - Optional router instance for navigation after logout
   */
  const logout = async (router?: any): Promise<void> => {
    if (isLoggingOut.value) return

    try {
      isLoggingOut.value = true
      lastAuthAction.value = 'logout'

      if (globalAuthStore.isAuthenticated) {
        await AuthAPI.logout()
      }

      // Clear global auth state
      await globalAuthStore.clearAuth()

      // Redirect to home page using Vue Router for SPA navigation if router is provided
      if (router) {
        await router.push('/')
      }
    } catch (err) {
      // Silently handle logout errors
    } finally {
      isLoggingOut.value = false
    }
  }

  /**
   * Update user profile
   * Delegates to global auth store
   */
  const updateUser = async (userData: Partial<User>): Promise<User> => {
    try {
      loading.value = true
      error.value = null

      const response = await AuthAPI.updateUser(userData)

      // Update global user state if successful
      if (response?.data) {
        // We only update the user object in global state, not the token
        globalAuthStore.setAuthState(response.data, globalAuthStore.token)
        return response.data
      }

      throw new Error('Failed to update user profile')
    } catch (err: any) {
      error.value = err.message || 'Failed to update profile'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Initialize authentication state
   * Delegates to global auth store
   */
  const initAuth = async (): Promise<void | boolean> => {
    return globalAuthStore.initAuth()
  }

  /**
   * Clear any auth errors
   */
  const clearError = (): void => {
    error.value = null
  }

  return {
    // State
    loading,
    error,
    isLoggingOut,
    lastAuthAction,

    // Computed properties that expose global state
    user,
    isAuthenticated,
    initialized,

    // Actions
    login,
    register,
    logout,
    updateUser,
    initAuth,
    clearError
  }
})
'''
    })

    # ===== Composable — verbatim from Imagi src/apps/auth/composables/useAuth.ts =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/composables/useAuth.ts',
        'type': 'typescript',
        'content': '''import { useAuthStore } from '../stores/index'
import type { User, LoginCredentials, UserRegistrationData, AuthResponse } from '../types/auth'

/**
 * Composable for accessing authentication functionality
 * Provides a clean interface to the auth module store
 */
export function useAuth() {
  const store = useAuthStore()

  return {
    // State
    user: store.user,
    isAuthenticated: store.isAuthenticated,
    loading: store.loading,
    error: store.error,
    isLoggingOut: store.isLoggingOut,
    lastAuthAction: store.lastAuthAction,
    initialized: store.initialized,

    // Actions
    login: store.login,
    logout: store.logout,
    register: store.register,
    updateUser: store.updateUser,
    initAuth: store.initAuth,
    clearError: store.clearError
  }
}

export type { User, LoginCredentials, UserRegistrationData, AuthResponse }
'''
    })

    # ===== Router — verbatim from Imagi src/apps/auth/router/index.ts =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/router/index.ts',
        'type': 'typescript',
        'content': '''import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/auth',
    component: () => import('../layouts/AuthLayout.vue'),
    children: [
      {
        path: 'signin',
        name: 'login',
        component: () => import('../views/Login.vue'),
        meta: {
          requiresAuth: false,
          layout: 'auth',
          title: 'Welcome Back',
          subtitle: 'Sign in to continue building amazing applications',
          badge: 'Secure Login',
          mainText: 'Looking to create an account?',
          mainLinkPath: '/auth/register',
          mainLinkText: 'Sign up'
        }
      },
      {
        path: 'register',
        name: 'register',
        component: () => import('../views/Register.vue'),
        meta: {
          requiresAuth: false,
          layout: 'auth',
          title: 'Create Account',
          subtitle: 'Start building your next great idea',
          badge: 'Get Started',
          mainText: 'Already have an account?',
          mainLinkPath: '/auth/signin',
          mainLinkText: 'Sign in'
        }
      }
    ]
  }
]

export { routes }
export default routes
'''
    })

    # ===== AuthLayout — Imagi design, adapted to be self-contained =====
    # (no DefaultLayout/ImagiLogo; media-query dark mode instead of :root.dark)
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/layouts/AuthLayout.vue',
        'type': 'vue',
        'content': '''<!-- Auth Layout - Clean minimal design matching Home page -->
<template>
  <!-- Clean full-screen layout -->
  <div class="min-h-screen bg-white dark:bg-[#0a0a0a] relative overflow-hidden transition-colors duration-500">
    <!-- Minimal background with subtle baby-blue wash -->
    <div class="fixed inset-0 pointer-events-none">
      <!-- Soft baby-blue gradient fade from the top -->
      <div class="absolute inset-x-0 top-0 h-[480px] bg-gradient-to-b from-blue-50/70 via-white to-white dark:from-blue-400/[0.06] dark:via-[#0a0a0a] dark:to-[#0a0a0a] transition-colors duration-500"></div>

      <!-- Very subtle grid pattern for texture (dark mode only) -->
      <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]"
           style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
    </div>

    <!-- Content wrapper with proper spacing -->
    <div class="flex min-h-screen w-full relative z-10">
      <div class="w-full flex items-center justify-center px-4 sm:px-6 py-16 pt-28 sm:pt-32">
        <!-- Clean Auth Container -->
        <div class="w-full max-w-[520px] mx-auto">
          <!-- Clean card with subtle shadow -->
          <div class="relative animate-fade-in">
            <div class="relative rounded-2xl border border-blue-200/70 dark:border-blue-300/[0.16] bg-white dark:bg-white/[0.05] crisp-card backdrop-blur-xl overflow-hidden transition-all duration-300">
              <!-- Card content -->
              <div class="relative z-10 p-8 sm:p-10">
                <!-- Logo and Title Section -->
                <div class="text-center mb-10">
                  <div class="inline-flex items-center justify-center mb-8">
                    <router-link to="/" class="text-3xl font-bold text-blue-950 dark:text-white transition-colors duration-300">
                      App
                    </router-link>
                  </div>

                  <!-- Title -->
                  <h2 class="text-xl sm:text-2xl font-semibold tracking-tight mb-3 leading-[1.2] text-blue-950 dark:text-white transition-colors duration-300">
                    {{ route.meta.title }}
                  </h2>
                  <p class="text-base text-blue-950/70 dark:text-blue-100/70 leading-relaxed transition-colors duration-300">
                    {{ route.meta.subtitle }}
                  </p>
                </div>

                <!-- Main Content with transition -->
                <router-view v-slot="{ Component }">
                  <transition name="fade" mode="out-in">
                    <component :is="Component" />
                  </transition>
                </router-view>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<style scoped>
/* Crisp, sharply-defined card: hairline edge + tight layered shadow */
.crisp-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

@media (prefers-color-scheme: dark) {
  .crisp-card {
    box-shadow:
      0 0 0 1px rgba(255, 255, 255, 0.04),
      0 1px 2px rgba(0, 0, 0, 0.5),
      0 4px 10px -2px rgba(0, 0, 0, 0.45),
      0 12px 28px -10px rgba(0, 0, 0, 0.55);
  }
}

/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Fade in animation */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.8s ease-out forwards;
}
</style>
'''
    })

    # ===== Login View — verbatim from Imagi src/apps/auth/views/Login.vue =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/views/Login.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="space-y-6">
    <Form v-slot="{ submitCount }" class="space-y-5" @submit="onSubmit">
      <!-- Username input with premium styling -->
      <div class="relative group">
        <Field name="username" rules="login_username" :validateOnBlur="false" v-slot="{ errorMessage, field }">
          <FormInput
            :modelValue="field.value || ''"
            @update:modelValue="field.onChange"
            @blur="field.onBlur"
            name="username"
            label="Username"
            icon="fas fa-user"
            placeholder="Enter your username"
            :disabled="authStore.loading || isSubmitting"
            :hasError="!!errorMessage && submitCount > 0"
          />
        </Field>
      </div>

      <!-- Password input with premium styling -->
      <div class="relative group">
        <Field name="password" rules="login_password" :validateOnBlur="false" v-slot="{ errorMessage, field }">
          <PasswordInput
            :modelValue="field.value || ''"
            @update:modelValue="field.onChange"
            @blur="field.onBlur"
            name="password"
            placeholder="Enter your password"
            :disabled="authStore.loading || isSubmitting"
            :hasError="!!errorMessage && submitCount > 0"
          />
        </Field>
      </div>

      <!-- Error message display -->
      <div class="space-y-5 pt-2">
        <transition name="fade-up">
          <div v-if="serverError"
               class="p-4 rounded-xl border border-red-500/20 bg-red-50 dark:bg-red-500/10 backdrop-blur-sm transition-colors duration-300">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-500/20 border border-red-200 dark:border-red-500/30 flex items-center justify-center flex-shrink-0 transition-colors duration-300">
                <i class="fas fa-exclamation-triangle text-red-600 dark:text-red-400 text-sm transition-colors duration-300"></i>
              </div>
              <p class="text-sm font-medium text-red-600 dark:text-red-400 whitespace-pre-line transition-colors duration-300">
                {{ serverError }}
              </p>
            </div>
          </div>
        </transition>

        <!-- Premium gradient button -->
        <GradientButton
          type="submit"
          :disabled="authStore.loading || isSubmitting"
          :loading="authStore.loading || isSubmitting"
          loading-text="Signing in..."
          class="w-full"
        >
          Sign In
        </GradientButton>
      </div>
    </Form>

    <!-- Auth Links -->
    <div class="text-center pt-2">
      <AuthLinks />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Form, Field, ErrorMessage } from 'vee-validate'
import { useAuthStore } from '@/apps/auth/stores/index'
import { formatAuthError } from '@/apps/auth/plugins/validation'
import type { LoginFormValues } from '@/apps/auth/types/form'

import {
  PasswordInput,
  FormInput,
  GradientButton,
  AuthLinks
} from '@/apps/auth/components'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const serverError = ref('')
const isSubmitting = ref(false)

// Clear any auth errors when component is unmounted
onBeforeUnmount(() => {
  authStore.clearError()
})

const onSubmit = async (values: LoginFormValues) => {
  serverError.value = ''
  isSubmitting.value = true

  try {
    // Get values from VeeValidate
    const username = values.username?.trim()
    const password = values.password?.trim()

    // Validate input - ensure both fields are filled
    if (!username || !password) {
      serverError.value = 'Username and password are required'
      isSubmitting.value = false
      return
    }

    const loginData = {
      username,
      password
    }

    // Show loading state in UI
    document.body.style.cursor = 'wait'

    await authStore.login(loginData)

    // Check if there's a redirect parameter to navigate to
    const redirectPath = route.query.redirect as string
    if (redirectPath) {
      await router.push(redirectPath)
    } else {
      // Default redirect to home
      await router.push({ path: '/' })
    }
  } catch (error: unknown) {
    serverError.value = formatAuthError(error, 'login')
  } finally {
    isSubmitting.value = false
    document.body.style.cursor = 'default'
  }
}
</script>

<style scoped>
/* Fade up transition for error messages */
.fade-up-enter-active,
.fade-up-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-up-enter-from,
.fade-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
'''
    })

    # ===== Register View — verbatim from Imagi src/apps/auth/views/Register.vue =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/views/Register.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="space-y-6">
    <Form v-slot="{ submitCount: formSubmitCount }" class="space-y-5" @submit="handleSubmit">
      <!-- Username input with premium styling -->
      <div class="relative group">
        <Field name="username" rules="required|username" :validateOnBlur="false" v-slot="{ errorMessage, field }">
          <FormInput
            :modelValue="field.value || ''"
            @update:modelValue="field.onChange"
            @blur="field.onBlur"
            name="username"
            label="Username"
            icon="fas fa-user"
            placeholder="Create a username (min. 3 characters)"
            :disabled="authStore.loading || isSubmitting"
            :hasError="!!errorMessage && formSubmitCount > 0"
          />
          <transition name="fade-up">
            <div v-if="errorMessage && formSubmitCount > 0" class="mt-2 text-sm text-red-400 flex items-center gap-2">
              <i class="fas fa-exclamation-circle text-xs"></i>
              <span>{{ errorMessage }}</span>
            </div>
          </transition>
        </Field>
      </div>

      <!-- Email input with premium styling -->
      <div class="relative group">
        <Field name="email" rules="required|email" :validateOnBlur="false" v-slot="{ errorMessage, field }">
          <FormInput
            :modelValue="field.value || ''"
            @update:modelValue="field.onChange"
            @blur="field.onBlur"
            name="email"
            label="Email"
            icon="fas fa-envelope"
            placeholder="Enter your email address"
            :disabled="authStore.loading || isSubmitting"
            :hasError="!!errorMessage && formSubmitCount > 0"
          />
          <transition name="fade-up">
            <div v-if="errorMessage && formSubmitCount > 0" class="mt-2 text-sm text-red-400 flex items-center gap-2">
              <i class="fas fa-exclamation-circle text-xs"></i>
              <span>{{ errorMessage }}</span>
            </div>
          </transition>
        </Field>
      </div>

      <!-- Password section -->
      <div class="space-y-4">
        <!-- Password input -->
        <div class="relative group">
          <Field name="password" rules="required|registration_password" :validateOnBlur="false" v-slot="{ errorMessage, field, value }">
            <PasswordInput
              :modelValue="field.value || ''"
              @update:modelValue="field.onChange"
              @blur="field.onBlur"
              name="password"
              placeholder="Create password"
              :disabled="authStore.loading || isSubmitting"
              :hasError="!!errorMessage && formSubmitCount > 0"
            />
            <!-- Password requirements with premium glass styling -->
            <div class="mt-4 p-4 rounded-xl
                        border border-blue-200/70 dark:border-white/[0.08]
                        bg-blue-50/50 dark:bg-white/[0.02]
                        backdrop-blur-sm
                        transition-all duration-300">
              <PasswordRequirements
                :password="value || ''"
                ref="passwordRequirements"
                class="text-sm"
              />
            </div>
          </Field>
        </div>

        <!-- Confirm password input -->
        <div class="relative group">
          <Field name="password_confirmation" rules="required|password_confirmation:@password" :validateOnBlur="false" v-slot="{ errorMessage, field }">
            <PasswordInput
              :modelValue="field.value || ''"
              @update:modelValue="field.onChange"
              @blur="field.onBlur"
              name="password_confirmation"
              placeholder="Confirm password"
              :disabled="authStore.loading || isSubmitting"
              :hasError="!!errorMessage && formSubmitCount > 0"
            />
            <transition name="fade-up">
              <div v-if="errorMessage && formSubmitCount > 0" class="mt-2 text-sm text-red-400 flex items-center gap-2">
                <i class="fas fa-exclamation-circle text-xs"></i>
                <span>{{ errorMessage }}</span>
              </div>
            </transition>
          </Field>
        </div>
      </div>

      <!-- Bottom section -->
      <div class="space-y-5 pt-2">
        <!-- Terms checkbox with premium styling -->
        <div class="p-4 rounded-xl
                    border border-blue-200/70 dark:border-white/[0.08]
                    bg-blue-50/50 dark:bg-white/[0.02]
                    backdrop-blur-sm
                    hover:bg-blue-50 dark:hover:bg-white/[0.04]
                    hover:border-blue-300/70 dark:hover:border-white/[0.12]
                    transition-all duration-300">
          <Field name="agreeToTerms" :rules="{ required: { allowFalse: false } }" :validateOnBlur="false" v-slot="{ errorMessage }">
            <FormCheckbox
              name="agreeToTerms"
              :disabled="authStore.loading || isSubmitting"
              :showError="false"
            >
              I agree to the
              <router-link to="/terms" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors duration-300 font-medium">
                Terms of Service
              </router-link>
              and
              <router-link to="/privacy" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 transition-colors duration-300 font-medium">
                Privacy Policy
              </router-link>
            </FormCheckbox>
            <div v-if="(errorMessage || !hasAcceptedTerms) && formSubmitCount > 0" class="mt-2 text-sm text-red-400 flex items-center gap-2">
              <i class="fas fa-exclamation-circle text-xs"></i>
              <span>You must accept the terms to continue</span>
            </div>
          </Field>
        </div>

        <!-- Error message with premium styling -->
        <transition name="fade-up">
          <div v-if="serverError"
               class="p-4 rounded-xl border border-red-500/20 bg-red-50 dark:bg-red-500/10 backdrop-blur-sm transition-colors duration-300">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-500/20 border border-red-200 dark:border-red-500/30 flex items-center justify-center flex-shrink-0 transition-colors duration-300">
                <i class="fas fa-exclamation-triangle text-red-600 dark:text-red-400 text-sm transition-colors duration-300"></i>
              </div>
              <p class="text-sm font-medium text-red-600 dark:text-red-400 whitespace-pre-line transition-colors duration-300">{{ serverError }}</p>
            </div>
          </div>
        </transition>

        <!-- Premium gradient button -->
        <GradientButton
          type="submit"
          :disabled="authStore.loading || isSubmitting"
          :loading="authStore.loading || isSubmitting"
          loading-text="Creating account..."
          class="w-full"
        >
          Create Account
        </GradientButton>
      </div>
    </Form>

    <!-- Auth Links -->
    <div class="text-center pt-2">
      <p class="text-blue-950/70 dark:text-blue-100/70 text-sm transition-colors duration-300">
        Already have an account?
        <router-link to="/auth/signin" class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 font-medium transition-colors duration-200 ml-1">
          Sign in
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { Form, Field } from 'vee-validate'
import { useAuthStore } from '@/apps/auth/stores/index'
import { formatAuthError } from '@/apps/auth/plugins/validation'
import type { RegisterFormValues, PasswordRequirementsRef } from '@/apps/auth/types/form'

import {
  PasswordInput,
  FormInput,
  FormCheckbox,
  PasswordRequirements,
  GradientButton,
} from '@/apps/auth/components'

const router = useRouter()
const authStore = useAuthStore()
const serverError = ref('')
const isSubmitting = ref(false)
const passwordRequirements = ref<PasswordRequirementsRef | null>(null)
const hasAcceptedTerms = ref(false)

defineOptions({
  name: 'Register'
})

// Clear any auth errors when component is unmounted
onBeforeUnmount(() => {
  authStore.clearError()
})

const handleSubmit = async (values: RegisterFormValues) => {
  serverError.value = ''
  isSubmitting.value = true

  try {
    // Get values from VeeValidate
    const username = values.username?.trim()
    const email = values.email?.trim()
    const password = values.password
    const passwordConfirmation = values.password_confirmation
    const agreeToTerms = values.agreeToTerms === true

    // Update terms acceptance state
    hasAcceptedTerms.value = agreeToTerms

    // Validate all required fields
    if (!username || !email || !password) {
      serverError.value = 'Please fill in all required fields'
      isSubmitting.value = false
      return
    }

    // Check terms acceptance first
    if (!agreeToTerms) {
      serverError.value = 'You must accept the Terms of Service and Privacy Policy to continue'
      isSubmitting.value = false
      return
    }

    // Check password confirmation matches
    if (password !== passwordConfirmation) {
      serverError.value = 'Passwords do not match'
      isSubmitting.value = false
      return
    }

    // Validate password length
    if (password.length < 8) {
      serverError.value = 'Password must be at least 8 characters long'
      isSubmitting.value = false
      return
    }

    // Create registration data
    const registerData = {
      username,
      email,
      password,
      password_confirmation: passwordConfirmation,
      terms_accepted: agreeToTerms
    }

    document.body.style.cursor = 'wait'

    await authStore.register(registerData)

    await router.push('/')
  } catch (error: unknown) {
    serverError.value = formatAuthError(error, 'register')
  } finally {
    isSubmitting.value = false
    document.body.style.cursor = 'default'
  }
}
</script>

<style scoped>
/* Fade up transition for error messages */
.fade-up-enter-active,
.fade-up-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-up-enter-from,
.fade-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
'''
    })

    # ===== Component index files — verbatim from Imagi =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/index.ts',
        'type': 'typescript',
        'content': '''// Re-export components by category
export * from './atoms'
export * from './molecules'
export * from './organisms'
'''
    })

    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/atoms/index.ts',
        'type': 'typescript',
        'content': '''// Input Components
export { default as PasswordInput } from './inputs/PasswordInput.vue'

// Button Components
export { default as GradientButton } from './buttons/GradientButton.vue'

// Auth Components
export { default as RequirementItem } from './items/RequirementItem.vue';
'''
    })

    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/molecules/index.ts',
        'type': 'typescript',
        'content': '''// Form Components
export { default as FormInput } from './forms/FormInput.vue'
export { default as FormCheckbox } from './forms/FormCheckbox.vue'

// Auth-specific Components
export { default as PasswordRequirements } from './messages/PasswordRequirements.vue';
export { default as AuthLinks } from './links/AuthLinks.vue';
export { default as SessionTimeoutWarning } from './messages/SessionTimeoutWarning.vue';
'''
    })

    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/organisms/index.ts',
        'type': 'typescript',
        'content': '''// Header Components
export { default as AuthHeader } from './headers/AuthHeader.vue';
'''
    })

    # ===== Atom Components — verbatim from Imagi =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/atoms/inputs/PasswordInput.vue',
        'type': 'vue',
        'content': '''<template>
  <div>
    <label v-if="label" :for="id" class="sr-only">{{ label }}</label>
    <div class="relative group">
      <span class="absolute inset-y-0 left-0 flex items-center pl-4 z-10">
        <i class="fas fa-lock text-blue-950/40 dark:text-blue-100/40 transition-colors duration-200"></i>
      </span>
      <input
        :id="id"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        @blur="onBlur"
        @change="onChange"
        :type="inputType"
        :name="name"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        class="w-full py-4 pl-12 pr-12 rounded-xl
               text-blue-950 dark:text-white
               placeholder-blue-950/40 dark:placeholder-white/30
               outline-none focus:outline-none
               disabled:opacity-50 disabled:cursor-not-allowed
               transition-all duration-200
               border bg-blue-50/50 dark:bg-white/[0.03] backdrop-blur-sm
               focus:ring-0"
        :class="{
          'border-red-500/50 bg-red-50 dark:bg-red-500/5': hasError,
          'border-blue-200/70 dark:border-white/[0.08]': !hasError
        }"
      >
      <button
        type="button"
        @click="togglePassword"
        class="absolute inset-y-0 right-0 flex items-center pr-4
               text-blue-950/40 dark:text-blue-100/40
               hover:text-blue-950 dark:hover:text-white
               transition-colors duration-200 z-10"
      >
        <i :class="['fas', isVisible ? 'fa-eye-slash' : 'fa-eye']"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const isVisible = ref(false)

const togglePassword = () => {
  isVisible.value = !isVisible.value
}

const inputType = computed(() => isVisible.value ? 'text' : 'password')

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  id: {
    type: String,
    default: () => `password-input-${Math.random().toString(36).substr(2, 9)}`
  },
  hasError: {
    type: Boolean,
    default: false
  },
  name: {
    type: String,
    default: 'password'
  },
  // Vee-validate field props
  onBlur: {
    type: Function,
    default: () => {}
  },
  onChange: {
    type: Function,
    default: () => {}
  }
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
/* Completely remove all focus styles and outlines */
input,
input:focus,
input:active,
input:focus-within,
input:focus-visible {
  outline: none !important;
  outline-width: 0 !important;
  outline-style: none !important;
  outline-color: transparent !important;
  box-shadow: none !important;
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  appearance: none !important;
}

/* Remove any ring effects */
input {
  --tw-ring-shadow: 0 0 #0000 !important;
  --tw-ring-offset-shadow: 0 0 #0000 !important;
  --tw-ring-color: transparent !important;
  --tw-ring-offset-color: transparent !important;
}

/* Remove browser default focus ring */
input::-moz-focus-inner {
  border: 0 !important;
}

/* Ensure button doesn't show outline either */
button,
button:focus,
button:active,
button:focus-visible {
  outline: none !important;
  outline-width: 0 !important;
  box-shadow: none !important;
}

/* Autofill styling for light mode */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus {
  -webkit-text-fill-color: #172554;
  -webkit-box-shadow: 0 0 0px 1000px rgba(239, 246, 255, 1) inset;
  transition: background-color 5000s ease-in-out 0s;
  border-color: rgb(191, 219, 254) !important;
}

/* Autofill styling for dark mode */
@media (prefers-color-scheme: dark) {
  input:-webkit-autofill,
  input:-webkit-autofill:hover,
  input:-webkit-autofill:focus {
    -webkit-text-fill-color: white;
    -webkit-box-shadow: 0 0 0px 1000px rgba(255, 255, 255, 0.03) inset;
    transition: background-color 5000s ease-in-out 0s;
    border-color: rgba(255, 255, 255, 0.08) !important;
  }
}
</style>
'''
    })

    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/atoms/buttons/GradientButton.vue',
        'type': 'vue',
        'content': '''<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="btn-3d btn-accent group relative w-full inline-flex items-center justify-center gap-2 px-8 py-4
           text-blue-950
           rounded-full
           font-medium
           border border-white/60 dark:border-white/30
           focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]
           transition-all duration-300
           disabled:opacity-50 disabled:cursor-not-allowed
           overflow-hidden"
  >
    <!-- Top edge highlight for 3D effect -->
    <span class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent"></span>
    <!-- Bottom edge shadow for depth -->
    <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-blue-900/15 to-transparent"></span>
    <!-- Content -->
    <span v-if="loading" class="relative z-10 flex items-center justify-center">
      <i class="fas fa-circle-notch fa-spin mr-2"></i>
      <span class="font-medium">{{ loadingText }}</span>
    </span>
    <span v-else class="relative z-10 flex items-center justify-center gap-2">
      <span class="font-medium"><slot></slot></span>
      <i class="fas fa-arrow-right text-sm transition-transform duration-300 group-hover:translate-x-1"></i>
    </span>
  </button>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'button'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: 'Loading...'
  }
})
</script>

<style scoped>
/* Soft 3D button effect - tight, layered, crisp. Blue-tinted shadows to suit the light baby-blue fill. */
.btn-3d {
  transform: translateY(0) translateZ(0);
  transition: transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease;
  box-shadow:
    0 1px 2px rgba(30, 58, 138, 0.14),
    0 4px 10px -2px rgba(30, 58, 138, 0.16),
    0 10px 20px -6px rgba(30, 58, 138, 0.18),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.12);
}

.btn-3d:active {
  transform: translateY(0) translateZ(0);
  transition-duration: 0.1s;
}

/* Soft baby-blue gradient fill */
.btn-accent {
  background: linear-gradient(155deg, #dbeeff 0%, #b7ddf7 55%, #9ecdf3 100%);
}

/* On dark, ground the light button with deep neutral shadows; keep the inner sheen */
@media (prefers-color-scheme: dark) {
  .btn-3d {
    box-shadow:
      0 1px 2px rgba(0, 0, 0, 0.5),
      0 4px 10px -2px rgba(0, 0, 0, 0.45),
      0 10px 20px -6px rgba(0, 0, 0, 0.5),
      inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
      inset 0 -2px 4px -1px rgba(30, 58, 138, 0.18);
  }
}
</style>
'''
    })

    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/atoms/items/RequirementItem.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="flex items-center gap-2.5">
    <div
      class="w-5 h-5 rounded-md flex items-center justify-center transition-all duration-300"
      :class="checked
        ? 'bg-emerald-500/20 border border-emerald-500/40'
        : 'bg-blue-100/60 dark:bg-white/[0.03] border border-blue-200/70 dark:border-white/[0.08]'"
    >
      <i
        class="fas text-[10px] transition-all duration-300"
        :class="checked
          ? 'fa-check text-emerald-500 dark:text-emerald-400'
          : 'fa-circle text-blue-950/20 dark:text-white/20'"
      ></i>
    </div>
    <span
      class="text-sm transition-colors duration-300"
      :class="checked ? 'text-blue-950/80 dark:text-white/80' : 'text-blue-950/40 dark:text-white/40'"
    >
      {{ text }}
    </span>
  </div>
</template>

<script setup>
defineProps({
  checked: {
    type: Boolean,
    default: false
  },
  text: {
    type: String,
    required: true
  }
})
</script>
'''
    })

    # ===== Molecule Components — verbatim from Imagi =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/molecules/forms/FormInput.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="form-group">
    <label class="relative block group">
      <span class="sr-only">{{ label }}</span>
      <span class="absolute inset-y-0 left-0 flex items-center pl-4 z-10">
        <i :class="[icon, 'text-blue-950/40 dark:text-blue-100/40 transition-colors duration-200']"></i>
      </span>
      <input
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        @blur="onBlur"
        @change="onChange"
        :name="name"
        :type="inputType"
        :disabled="disabled"
        :placeholder="placeholder"
        class="w-full py-4 pl-12 pr-4 rounded-xl
               text-blue-950 dark:text-white
               placeholder-blue-950/40 dark:placeholder-white/30
               outline-none focus:outline-none
               disabled:opacity-50 disabled:cursor-not-allowed
               transition-all duration-200
               border bg-blue-50/50 dark:bg-white/[0.03] backdrop-blur-sm
               focus:ring-0"
        :class="{
          'border-red-500/50 bg-red-50 dark:bg-red-500/5': hasError,
          'border-blue-200/70 dark:border-white/[0.08]': !hasError
        }"
      >
    </label>
    <ErrorMessage v-if="showError" :name="name" class="mt-2 text-sm text-red-400 flex items-center gap-2">
      <i class="fas fa-exclamation-circle text-xs"></i>
    </ErrorMessage>
  </div>
</template>

<script setup>
import { ErrorMessage } from 'vee-validate'
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  name: {
    type: String,
    required: true
  },
  label: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'text'
  },
  icon: {
    type: String,
    required: true
  },
  disabled: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: ''
  },
  showError: {
    type: Boolean,
    default: true
  },
  hasError: {
    type: Boolean,
    default: false
  },
  // Vee-validate field props
  onBlur: {
    type: Function,
    default: () => {}
  },
  onChange: {
    type: Function,
    default: () => {}
  }
})

defineEmits(['update:modelValue'])

const inputType = computed(() => {
  return props.type
})
</script>

<style scoped>
/* Completely remove all focus styles and outlines */
input,
input:focus,
input:active,
input:focus-within,
input:focus-visible {
  outline: none !important;
  outline-width: 0 !important;
  outline-style: none !important;
  outline-color: transparent !important;
  box-shadow: none !important;
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  appearance: none !important;
}

/* Remove any ring effects */
input {
  --tw-ring-shadow: 0 0 #0000 !important;
  --tw-ring-offset-shadow: 0 0 #0000 !important;
  --tw-ring-color: transparent !important;
  --tw-ring-offset-color: transparent !important;
}

/* Remove browser default focus ring */
input::-moz-focus-inner {
  border: 0 !important;
}

/* Autofill styling for light mode */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus {
  -webkit-text-fill-color: #172554;
  -webkit-box-shadow: 0 0 0px 1000px rgba(239, 246, 255, 1) inset;
  transition: background-color 5000s ease-in-out 0s;
  border-color: rgb(191, 219, 254) !important;
}

/* Autofill styling for dark mode */
@media (prefers-color-scheme: dark) {
  input:-webkit-autofill,
  input:-webkit-autofill:hover,
  input:-webkit-autofill:focus {
    -webkit-text-fill-color: white;
    -webkit-box-shadow: 0 0 0px 1000px rgba(255, 255, 255, 0.03) inset;
    transition: background-color 5000s ease-in-out 0s;
    border-color: rgba(255, 255, 255, 0.08) !important;
  }
}
</style>
'''
    })

    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/molecules/forms/FormCheckbox.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="flex items-start">
    <div class="flex items-center h-5">
      <Field
        :name="name"
        type="checkbox"
        :value="true"
        v-slot="{ field }"
      >
        <input
          type="checkbox"
          v-bind="field"
          :disabled="disabled"
          class="w-4 h-4 rounded
                 accent-blue-600
                 border-blue-300 dark:border-white/20
                 bg-blue-50 dark:bg-white/[0.05]
                 text-blue-600 focus:ring-blue-500/40 focus:ring-offset-0 focus:ring-2
                 disabled:opacity-50 disabled:cursor-not-allowed
                 transition-all duration-300
                 checked:bg-blue-600 checked:border-blue-600"
        >
      </Field>
    </div>
    <div class="ml-3">
      <label class="text-sm text-blue-950/60 dark:text-white/60 leading-relaxed">
        <slot></slot>
      </label>
      <ErrorMessage v-if="showError && false" :name="name" class="block mt-1 text-sm text-red-400" />
    </div>
  </div>
</template>

<script setup>
import { Field, ErrorMessage } from 'vee-validate'

defineProps({
  name: {
    type: String,
    required: true
  },
  disabled: {
    type: Boolean,
    default: false
  },
  showError: {
    type: Boolean,
    default: true
  }
})
</script>
'''
    })

    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/molecules/messages/PasswordRequirements.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="w-full">
    <!-- Requirements Grid -->
    <div class="grid grid-cols-2 gap-x-8 gap-y-2">
      <!-- Left column -->
      <div class="space-y-2">
        <RequirementItem
          :checked="hasMinLength"
          text="8+ characters"
        />
        <RequirementItem
          :checked="hasUpperCase"
          text="One uppercase"
        />
        <RequirementItem
          :checked="hasLowerCase"
          text="One lowercase"
        />
      </div>

      <!-- Right column -->
      <div class="space-y-2">
        <RequirementItem
          :checked="hasNumber"
          text="One number"
        />
        <RequirementItem
          :checked="hasSpecialChar"
          text="One symbol"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RequirementItem } from '@/apps/auth/components'

const props = defineProps({
  password: {
    type: String,
    required: true,
    default: ''
  }
})

const hasMinLength = computed(() => (props.password || '').length >= 8)
const hasUpperCase = computed(() => /[A-Z]/.test(props.password || ''))
const hasLowerCase = computed(() => /[a-z]/.test(props.password || ''))
const hasNumber = computed(() => /\\d/.test(props.password || ''))
const hasSpecialChar = computed(() => /[!@#$%^&*(),.?":{}|<>]/.test(props.password || ''))

const isValid = computed(() =>
  hasMinLength.value &&
  hasUpperCase.value &&
  hasLowerCase.value &&
  hasNumber.value &&
  hasSpecialChar.value
)

defineExpose({ isValid })
</script>
'''
    })

    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/molecules/links/AuthLinks.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="space-y-4">
    <!-- Enhanced Links Section -->
    <div class="text-center">
      <!-- Alternate Auth Action -->
      <p class="text-blue-950/70 dark:text-blue-100/70 text-sm transition-colors duration-300">
        <template v-if="isLoginPage">
          New here?
          <router-link
            to="/auth/register"
            class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 font-medium transition-colors duration-200 ml-1"
          >
            Create an account
          </router-link>
        </template>
        <template v-else>
          Already have an account?
          <router-link
            to="/auth/signin"
            class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 font-medium transition-colors duration-200 ml-1"
          >
            Sign in here
          </router-link>
        </template>
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isLoginPage = computed(() => route.path === '/auth/signin')
</script>
'''
    })

    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/molecules/messages/SessionTimeoutWarning.vue',
        'type': 'vue',
        'content': '''<template>
  <div
    v-if="showWarning"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
  >
    <div class="bg-dark-800 p-6 rounded-lg max-w-md w-full mx-4">
      <div class="text-center">
        <svg
          class="w-12 h-12 text-yellow-500 mx-auto mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>

        <h2 class="text-xl font-semibold text-white mb-2">
          Session Timeout Warning
        </h2>

        <p class="text-gray-400 mb-4">
          Your session will expire in {{ timeLeft }} minutes. Would you like to stay signed in?
        </p>

        <div class="flex justify-center space-x-4">
          <button
            @click="extendSession"
            class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors"
          >
            Stay Signed In
          </button>

          <button
            @click="logout"
            class="px-4 py-2 bg-dark-700 hover:bg-dark-600 text-gray-300 rounded-lg transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/shared/stores/auth'

const authStore = useAuthStore()
const showWarning = ref(false)
const timeLeft = ref(5)
let warningTimer: number | null = null
let countdownTimer: number | null = null

const WARNING_THRESHOLD = 5 * 60 * 1000 // 5 minutes before timeout
const COUNTDOWN_INTERVAL = 60 * 1000 // 1 minute

const startWarningTimer = () => {
  const sessionTimeout = authStore.sessionTimeout
  if (sessionTimeout) {
    const timeUntilWarning = sessionTimeout - WARNING_THRESHOLD
    warningTimer = window.setTimeout(() => {
      showWarning.value = true
      startCountdown()
    }, timeUntilWarning)
  }
}

const startCountdown = () => {
  timeLeft.value = 5
  countdownTimer = window.setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) {
      logout()
    }
  }, COUNTDOWN_INTERVAL)
}

const extendSession = async () => {
  try {
    await authStore.refreshToken()
    showWarning.value = false
    resetTimers()
    startWarningTimer()
  } catch (error) {
    // Failed to extend session - logout user
    logout()
  }
}

const logout = () => {
  authStore.logout()
  resetTimers()
}

const resetTimers = () => {
  if (warningTimer) {
    clearTimeout(warningTimer)
    warningTimer = null
  }
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

onMounted(() => {
  startWarningTimer()
})

onUnmounted(() => {
  resetTimers()
})
</script>
'''
    })

    # ===== Organism Components — verbatim from Imagi (brand copy neutralized) =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/organisms/headers/AuthHeader.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="text-center mb-8">
    <div class="brand-header mb-6">
      <div class="logo-container inline-flex items-center justify-center p-3 rounded-2xl bg-gradient-to-br from-primary-500/10 to-violet-500/10 border border-primary-500/20 mb-6">
        <h1 class="text-3xl font-bold bg-gradient-to-r from-primary-400 to-violet-400 bg-clip-text text-transparent">
          App
        </h1>
      </div>
      <h2 class="text-2xl font-bold text-white mb-2">{{ title }}</h2>
      <p class="text-gray-400">{{ subtitle }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuthHeader',
  props: {
    title: {
      type: String,
      required: true
    },
    subtitle: {
      type: String,
      required: true
    }
  }
}
</script>
'''
    })

    # ========== Backend Files ==========
    # Verbatim copies of Imagi's apps/Auth, at the generated project's
    # lowercase apps.auth path (hence the explicit 'user_auth' label).

    files.append({
        'name': 'backend/django/apps/auth/__init__.py',
        'type': 'python',
        'content': ''
    })

    files.append({
        'name': 'backend/django/apps/auth/apps.py',
        'type': 'python',
        'content': '''from django.apps import AppConfig

class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.auth'
    # Explicit label: the default ('auth') collides with django.contrib.auth
    label = 'user_auth'
'''
    })

    files.append({
        'name': 'backend/django/apps/auth/migrations/__init__.py',
        'type': 'python',
        'content': ''
    })

    files.append({
        'name': 'backend/django/apps/auth/api/__init__.py',
        'type': 'python',
        'content': ''
    })

    files.append({
        'name': 'backend/django/apps/auth/api/serializers.py',
        'type': 'python',
        'content': '''from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'name', 'balance',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'balance')

    def get_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_balance(self, obj):
        # TODO: wire to billing model when it exists
        return 0

    def get_updated_at(self, obj):
        dt = obj.last_login or obj.date_joined
        return dt.isoformat() if dt else None


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirmation = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'A user with this username already exists.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                'A user with this email already exists.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirmation']:
            raise serializers.ValidationError(
                {'password_confirmation': 'Passwords do not match.'})
        try:
            validate_password(attrs['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirmation', None)
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
'''
    })

    files.append({
        'name': 'backend/django/apps/auth/api/views.py',
        'type': 'python',
        'content': '''from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import RegisterSerializer, UserSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_view(request):
    """Plant the csrftoken cookie for the Vue SPA."""
    get_token(request)
    return Response({'detail': 'CSRF cookie set'})


@api_view(['POST'])
@permission_classes([AllowAny])
def signin_view(request):
    username = (request.data.get('username') or '').strip()
    password = request.data.get('password') or ''
    if not username or not password:
        return Response(
            {'detail': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response(
            {'detail': 'Invalid username or password.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    login(request, user)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    login(request, user)
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {'token': token.key, 'user': UserSerializer(user).data},
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
    except (Token.DoesNotExist, AttributeError):
        pass
    logout(request)
    return Response({'detail': 'Successfully logged out.'})


@api_view(['GET'])
@permission_classes([AllowAny])
def init_view(request):
    if request.user.is_authenticated:
        return Response({
            'isAuthenticated': True,
            'user': UserSerializer(request.user).data,
        })
    return Response({'isAuthenticated': False, 'user': None})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def user_update_view(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data)
'''
    })

    files.append({
        'name': 'backend/django/apps/auth/api/urls.py',
        'type': 'python',
        'content': '''from django.urls import path

from .views import (
    csrf_view,
    init_view,
    logout_view,
    register_view,
    signin_view,
    user_update_view,
)

app_name = 'auth_api'

urlpatterns = [
    path('csrf/', csrf_view, name='csrf'),
    path('signin/', signin_view, name='signin'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('init/', init_view, name='init'),
    path('user/', user_update_view, name='user-update'),
]
'''
    })

    files.append({
        'name': 'backend/django/apps/auth/tests.py',
        'type': 'python',
        'content': '''"""
Tests for the Auth app.

Covers the registration/user serializers and every authentication API
endpoint (csrf, signin, register, logout, init, user-update).
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.auth.api.serializers import RegisterSerializer, UserSerializer

User = get_user_model()


class RegisterSerializerTests(APITestCase):
    """Validation rules enforced by RegisterSerializer."""

    def _base_data(self, **overrides):
        data = {
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'sup3rSecret!',
            'password_confirmation': 'sup3rSecret!',
        }
        data.update(overrides)
        return data

    def test_valid_payload_creates_user(self):
        serializer = RegisterSerializer(data=self._base_data())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.username, 'alice')
        self.assertEqual(user.email, 'alice@example.com')
        # Password must be hashed, never stored in the clear.
        self.assertTrue(user.check_password('sup3rSecret!'))
        self.assertNotEqual(user.password, 'sup3rSecret!')

    def test_password_mismatch_is_rejected(self):
        serializer = RegisterSerializer(
            data=self._base_data(password_confirmation='different!')
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_confirmation', serializer.errors)

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user(username='alice', password='whatever123')
        serializer = RegisterSerializer(data=self._base_data())
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

    def test_duplicate_email_is_rejected_case_insensitively(self):
        User.objects.create_user(
            username='bob', email='ALICE@example.com', password='whatever123'
        )
        serializer = RegisterSerializer(data=self._base_data())
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_weak_password_is_rejected(self):
        serializer = RegisterSerializer(
            data=self._base_data(password='password', password_confirmation='password')
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)


class UserSerializerTests(APITestCase):
    """Read-only representation returned to the SPA."""

    def test_name_falls_back_to_username(self):
        user = User.objects.create_user(username='carol', password='whatever123')
        data = UserSerializer(user).data
        self.assertEqual(data['name'], 'carol')
        self.assertEqual(data['balance'], 0)
        self.assertEqual(data['username'], 'carol')

    def test_name_uses_full_name_when_available(self):
        user = User.objects.create_user(
            username='dave', password='whatever123',
            first_name='Dave', last_name='Smith',
        )
        data = UserSerializer(user).data
        self.assertEqual(data['name'], 'Dave Smith')

    def test_balance_and_id_are_read_only(self):
        user = User.objects.create_user(username='erin', password='whatever123')
        serializer = UserSerializer(
            user, data={'balance': 999, 'username': 'erin2'}, partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        # username is writable, balance is not.
        self.assertEqual(updated.username, 'erin2')
        self.assertEqual(UserSerializer(updated).data['balance'], 0)


class SigninViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('auth_api:signin')
        self.user = User.objects.create_user(
            username='frank', email='frank@example.com', password='correct-horse-9'
        )

    def test_valid_credentials_return_token_and_user(self):
        resp = self.client.post(
            self.url, {'username': 'frank', 'password': 'correct-horse-9'}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('token', resp.data)
        self.assertEqual(resp.data['user']['username'], 'frank')
        # A token row must be created and match the returned key.
        token = Token.objects.get(user=self.user)
        self.assertEqual(token.key, resp.data['token'])

    def test_wrong_password_returns_401(self):
        resp = self.client.post(
            self.url, {'username': 'frank', 'password': 'wrong'}
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_missing_fields_return_400(self):
        resp = self.client.post(self.url, {'username': 'frank'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signin_is_idempotent_on_token(self):
        first = self.client.post(
            self.url, {'username': 'frank', 'password': 'correct-horse-9'}
        )
        second = self.client.post(
            self.url, {'username': 'frank', 'password': 'correct-horse-9'}
        )
        self.assertEqual(first.data['token'], second.data['token'])


class RegisterViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('auth_api:register')

    def test_register_creates_user_and_returns_token(self):
        resp = self.client.post(self.url, {
            'username': 'grace',
            'email': 'grace@example.com',
            'password': 'sup3rSecret!',
            'password_confirmation': 'sup3rSecret!',
        })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', resp.data)
        self.assertEqual(resp.data['user']['username'], 'grace')
        self.assertTrue(User.objects.filter(username='grace').exists())

    def test_register_with_invalid_data_returns_400(self):
        resp = self.client.post(self.url, {
            'username': 'grace',
            'email': 'not-an-email',
            'password': 'x',
            'password_confirmation': 'y',
        })
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='grace').exists())


class LogoutViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('auth_api:logout')
        self.user = User.objects.create_user(username='heidi', password='correct-horse-9')
        self.token = Token.objects.create(user=self.user)

    def test_logout_requires_authentication(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_deletes_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(user=self.user).exists())


class InitViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('auth_api:init')
        self.user = User.objects.create_user(username='ivan', password='correct-horse-9')

    def test_unauthenticated_reports_not_authenticated(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(resp.data['isAuthenticated'])
        self.assertIsNone(resp.data['user'])

    def test_authenticated_returns_user(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data['isAuthenticated'])
        self.assertEqual(resp.data['user']['username'], 'ivan')


class UserUpdateViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('auth_api:user-update')
        self.user = User.objects.create_user(
            username='judy', email='judy@example.com', password='correct-horse-9'
        )

    def test_update_requires_authentication(self):
        resp = self.client.patch(self.url, {'email': 'new@example.com'})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_update_email(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        resp = self.client.patch(self.url, {'email': 'new@example.com'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'new@example.com')
'''
    })

    return files
