"""
Prebuilt app templates for Imagi Builder.
Generates both frontend (Vue) and backend (Django) files for default apps: home, auth, payments.

All file paths returned are relative to the project's root, so they can be written
with FileService.create_file as-is.
"""
from __future__ import annotations

from typing import Dict, List

# ---- Shared helpers ----

def _frontend_scaffold(app_name: str, cap_name: str, welcome: str) -> List[Dict[str, str]]:
    return [
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/index.ts',
            'type': 'typescript',
            'content': """// {cap} app entry point
export * from './router'
export * from './stores'
export * from './components'
export * from './views'
""".replace('{cap}', cap_name),
        },
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/router/index.ts',
            'type': 'typescript',
            'content': f"""import type {{ RouteRecordRaw }} from 'vue-router'
import {cap_name}View from '../views/{cap_name}View.vue'

const routes: RouteRecordRaw[] = [
  {{
    path: '/{app_name}',
    name: '{app_name}-view',
    component: {cap_name}View,
    meta: {{ requiresAuth: false, title: '{cap_name}' }}
  }}
]

export {{ routes }}
""",
        },
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/stores/index.ts',
            'type': 'typescript',
            'content': "export * from './{app_name}'\n".format(app_name=app_name),
        },
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/stores/{app_name}.ts',
            'type': 'typescript',
            'content': f"""import {{ defineStore }} from 'pinia'
import {{ ref }} from 'vue'

export const use{cap_name}Store = defineStore('{app_name}', () => {{
  const loading = ref(false)
  const setLoading = (v: boolean) => (loading.value = v)
  return {{ loading, setLoading }}
}})
""",
        },
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/components/index.ts',
            'type': 'typescript',
            'content': "export * from './atoms'\nexport * from './molecules'\nexport * from './organisms'\n",
        },
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/components/atoms/index.ts',
            'type': 'typescript',
            'content': '// atoms\n',
        },
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/components/molecules/index.ts',
            'type': 'typescript',
            'content': '// molecules\n',
        },
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/components/organisms/index.ts',
            'type': 'typescript',
            'content': '// organisms\n',
        },
        {
            'name': f'frontend/vuejs/src/apps/{app_name}/views/{cap_name}View.vue',
            'type': 'vue',
            'content': f"""<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-12">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-16">
        <h1 class="text-5xl font-bold text-gray-900 mb-6">{cap_name} App</h1>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto">{welcome}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>
""",
        },
        {
            'name': f"frontend/vuejs/src/apps/{app_name}/views/index.ts",
            'type': 'typescript',
            'content': f"export {{ default as {cap_name}View }} from './{cap_name}View.vue'\n",
        },
    ]


def _backend_scaffold(app_name: str, cap_name: str) -> List[Dict[str, str]]:
    app_module = f"apps.{app_name}"
    return [
        {
            'name': f'backend/django/apps/{app_name}/__init__.py',
            'type': 'python',
            'content': '',
        },
        {
            'name': f'backend/django/apps/{app_name}/apps.py',
            'type': 'python',
            'content': (
                "from django.apps import AppConfig\n\n"
                f"class {cap_name.capitalize()}Config(AppConfig):\n"
                "    default_auto_field = 'django.db.models.BigAutoField'\n"
                f"    name = '{app_module}'\n"
            ),
        },
        {
            'name': f'backend/django/apps/{app_name}/models.py',
            'type': 'python',
            'content': "from django.db import models\n\n# Add your models here.\n",
        },
        {
            'name': f'backend/django/apps/{app_name}/serializers.py',
            'type': 'python',
            'content': "from rest_framework import serializers\n\n# Add your serializers here.\n",
        },
        {
            'name': f'backend/django/apps/{app_name}/views.py',
            'type': 'python',
            'content': (
                "from rest_framework.decorators import api_view\n"
                "from rest_framework.response import Response\n"
                "from rest_framework import status\n\n"
                "@api_view(['GET'])\n"
                "def health(_request):\n"
                f"    return Response({{'app': '{app_name}', 'status': 'ok'}}, status=status.HTTP_200_OK)\n"
            ),
        },
        {
            'name': f'backend/django/apps/{app_name}/urls.py',
            'type': 'python',
            'content': (
                "from django.urls import path\n"
                "from . import views\n\n"
                "urlpatterns = [\n"
                "    path('health/', views.health, name='health'),\n"
                "]\n"
            ),
        },
        {
            'name': f'backend/django/apps/{app_name}/admin.py',
            'type': 'python',
            'content': "from django.contrib import admin\n\n# Register your models here.\n",
        },
        {
            'name': f'backend/django/apps/{app_name}/tests.py',
            'type': 'python',
            'content': (
                "from django.test import TestCase\n\n"
                "class BasicTest(TestCase):\n"
                "    def test_health(self):\n"
                "        self.assertTrue(True)\n"
            ),
        },
    ]

# ---- App-specific additions ----

def home_app_files() -> List[Dict[str, str]]:
    app_name = 'home'
    cap = 'Home'
    welcome = 'Welcome to your project home app.'
    files: List[Dict[str, str]] = []
    files += _frontend_scaffold(app_name, cap, welcome)
    files += _backend_scaffold(app_name, cap)
    return files


def auth_app_files() -> List[Dict[str, str]]:
    """
    Generate comprehensive authentication app files with full Login/Register functionality.
    Based on the Imagi main auth app structure.
    """
    app_name = 'auth'
    files: List[Dict[str, str]] = []
    
    # ========== Frontend Files ==========
    
    # Main index.ts
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/index.ts',
        'type': 'typescript',
        'content': '''// Auth app entry point
export * from './router'
export * from './stores'
export * from './components'
export * from './views'
'''
    })
    
    # ===== Types =====
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
    
    # ===== Services =====
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
import axios from 'axios'

// API Configuration
const API_PATH = '/v1/auth'

// Helper function to get CSRF token from cookies
function getCookie(name: string): string | null {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
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
  async getCSRFToken() {
    try {
      const response = await axios.get(`${API_PATH}/csrf/`, {
        timeout: 30000,
      })
      return response
    } catch (error: any) {
      console.error('CSRF token request failed:', error.message)
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
        console.error('Error fetching CSRF token:', error.message)
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
      
      const response = await api.post(`${API_PATH}/login/`, credentials, {
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
        const errorMessage = error.response.data?.non_field_errors?.[0] || 
                           error.response.data?.detail || 
                           'Invalid username or password'
        throw new Error(errorMessage)
      } else if (error.response?.status === 401) {
        throw new Error('Invalid username or password')
      } else if (error.response?.status === 429) {
        throw new Error('Too many login attempts. Please try again later.')
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
      
      if (!userData.terms_accepted) {
        throw new Error('You must accept the terms and conditions')
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
      
      const response = await api.post(fullRequestUrl, userData, {
        headers,
        timeout: 30000
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
          throw new Error(`Username: ${errorData.username[0]}`)
        }
        if (errorData.email) {
          throw new Error(`Email: ${errorData.email[0]}`)
        }
        if (errorData.password) {
          throw new Error(`Password: ${errorData.password[0]}`)
        }
        if (errorData.non_field_errors) {
          throw new Error(errorData.non_field_errors[0])
        }
        
        // Generic validation error
        throw new Error('Please check your input and try again')
      }
      
      // Handle other HTTP errors
      if (error.response?.status === 409) {
        throw new Error('An account with this email or username already exists')
      }
      
      if (error.response?.status === 429) {
        throw new Error('Too many registration attempts. Please try again later.')
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
    } catch (error) {
      console.error('Logout error:', error)
      throw error
    } finally {
      logoutPromise = null
    }
  },

  async updateUser(userData: Partial<User>): Promise<{ data: User }> {
    const response = await api.patch(`${API_PATH}/user/`, userData)
    return response
  },

  async healthCheck(): Promise<{ data: { status: string; service: string; database: string } }> {
    try {
      const response = await api.get(`${API_PATH}/health/`, {
        timeout: 5000
      })
      return response
    } catch (error: any) {
      console.error('Health check failed:', error.message)
      throw error
    }
  }
}
'''
    })
    
    # Continue with part 2...
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

// Simple username validation
defineRule('username', () => true)

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

const errorMessages = {
  'This username is already taken. Please choose another one.': 'This username is already taken. Please try another one.',
  'A user is already registered with this e-mail address.': 'This email is already registered. Please use another one or sign in.',
  'Password must be at least 8 characters long': 'Password must be at least 8 characters long.',
  'Passwords don\\'t match': 'Passwords don\\'t match. Please make sure they are identical.',
  'Unable to complete registration. Please try again.': 'Unable to complete registration. Please try again.',
  'No account found with this username': 'No account found with this username. Please check your spelling or create an account.',
  'Invalid password. Please try again': 'Incorrect password. Please try again.',
  'This account has been disabled': 'This account has been disabled. Please contact support.',
  'Unable to log in with provided credentials.': 'Invalid username or password. Please try again.',
  'Username is required': 'Username is required.',
  'Password is required': 'Password is required.',
  'Not found.': 'Account not found. Please check your username.',
  'Authentication credentials were not provided.': 'Please enter your login credentials.',
  'Invalid credentials': 'Username or password is incorrect.',
  'Login failed. Please try again later': 'Login failed. Please try again later.',
  'Login failed: No token received': 'Unable to log in. Please try again.',
  'Network Error': 'Unable to connect to server. Please check your internet connection.',
  'Login failed: Please try again': 'Login failed. Please try again later.',
  'Login failed: Invalid response format': 'Unable to complete login. Please try again.',
  'Invalid server response: Missing token': 'Unable to complete login. Please try again.',
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
      
      // Check for different error formats
      if (responseData.error) {
        return errorMessages[responseData.error as keyof typeof errorMessages] || responseData.error
      }
      
      if (responseData.detail) {
        if (typeof responseData.detail === 'object') {
          const errorMessages = []
          
          for (const [field, message] of Object.entries(responseData.detail)) {
            if (field === 'non_field_errors' || field === 'error') {
              errorMessages.push(message)
            } else {
              errorMessages.push(`${field}: ${message}`)
            }
          }
          
          return errorMessages.join('\\n')
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
    
    # Stores
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/stores/index.ts',
        'type': 'typescript',
        'content': '''import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { AuthAPI } from '../services/api'
import { useAuthStore as useGlobalAuthStore } from '@/shared/stores/auth'
import type { LoginCredentials, AuthResponse, UserRegistrationData, User } from '../types/auth'

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
  const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
    try {
      loading.value = true
      error.value = null
      lastAuthAction.value = 'login'
      
      const response = await AuthAPI.login(credentials)
      
      if (response?.data?.token) {
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

  const register = async (userData: UserRegistrationData): Promise<AuthResponse> => {
    try {
      loading.value = true
      error.value = null
      lastAuthAction.value = 'register'
      
      const response = await AuthAPI.register(userData)
      
      if (response?.data?.token) {
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

  const logout = async (router?: any): Promise<void> => {
    if (isLoggingOut.value) return

    try {
      isLoggingOut.value = true
      lastAuthAction.value = 'logout'
      
      if (globalAuthStore.isAuthenticated) {
        await AuthAPI.logout()
      }
      
      await globalAuthStore.clearAuth()
      
      if (router) {
        await router.push('/')
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      isLoggingOut.value = false
    }
  }

  const updateUser = async (userData: Partial<User>): Promise<User> => {
    try {
      loading.value = true
      error.value = null
      
      const response = await AuthAPI.updateUser(userData)
      
      if (response?.data) {
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

  const initAuth = async (): Promise<void | boolean> => {
    return globalAuthStore.initAuth()
  }

  const clearError = (): void => {
    error.value = null
  }

  return {
    loading,
    error,
    isLoggingOut,
    lastAuthAction,
    user,
    isAuthenticated,
    initialized,
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
    
    # Router
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
        path: 'login',
        name: 'login',
        component: () => import('../views/Login.vue'),
        meta: {
          requiresAuth: false,
          layout: 'auth',
          title: 'Welcome Back',
          subtitle: 'Sign in to your account'
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
          subtitle: 'Get started today'
        }
      }
    ]
  }
]

export { routes }
export default routes
'''
    })
    
    # Views index
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/views/index.ts',
        'type': 'typescript',
        'content': '''export { default as Login } from './Login.vue'
export { default as Register } from './Register.vue'
'''
    })
    
    # Login View
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/views/Login.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="space-y-5">
    <Form v-slot="{ errors: formErrors, submitCount, submitForm, values }" class="space-y-6" @submit="onSubmit">
      <!-- Username input -->
      <div class="relative">
        <Field name="username" rules="login_username" :validateOnBlur="false" v-slot="{ errorMessage, field }">
          <FormInput
            v-bind="field"
            name="username"
            label="Username"
            icon="fas fa-user"
            placeholder="Enter your username"
            :disabled="authStore.loading || isSubmitting"
            :hasError="!!errorMessage && submitCount > 0"
            v-model="formData.username"
            class="auth-input min-h-[42px] sm:min-h-[48px] shadow-sm hover:shadow-md transition-shadow duration-300"
          />
        </Field>
      </div>

      <!-- Password input -->
      <div class="relative">
        <Field name="password" rules="login_password" :validateOnBlur="false" v-slot="{ errorMessage, field }">
          <PasswordInput
            v-bind="field"
            name="password"
            v-model="formData.password"
            placeholder="Enter your password"
            :disabled="authStore.loading || isSubmitting"
            :hasError="!!errorMessage && submitCount > 0"
            class="auth-input min-h-[42px] sm:min-h-[48px] shadow-sm hover:shadow-md transition-shadow duration-300"
          />
        </Field>
      </div>

      <!-- Error message -->
      <div class="space-y-5 pt-2">
        <transition name="fade-up">
          <div v-if="serverError" 
               class="p-4 bg-red-500/20 border border-red-400/40 rounded-xl backdrop-blur-sm shadow-lg shadow-red-500/10">
            <p class="text-sm font-medium text-red-100 text-center">{{ serverError }}</p>
          </div>
        </transition>

        <!-- Submit button -->
        <GradientButton
          type="submit"
          :disabled="authStore.loading || isSubmitting"
          :loading="authStore.loading || isSubmitting"
          loading-text="Signing in..."
          class="w-full min-h-[48px] sm:min-h-[52px] mt-4"
        >
          Sign In
        </GradientButton>
      </div>
    </Form>

    <!-- Auth Links -->
    <div class="pt-4">
      <AuthLinks />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Form, Field } from 'vee-validate'
import { useAuthStore } from '@/apps/auth/stores/index'
import { formatAuthError } from '@/apps/auth/plugins/validation'
import type { LoginFormValues } from '@/apps/auth/types/form'
import { AuthAPI } from '@/apps/auth/services/api'

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

const formData = reactive({
  username: '',
  password: ''
})

onMounted(async () => {
  try {
    const healthResponse = await AuthAPI.healthCheck()
    console.log('Auth service health check:', healthResponse.data)
  } catch (error) {
    console.error('Auth service health check failed:', error)
  }
})

watch([() => formData.username, () => formData.password], () => {
  if (serverError.value) {
    serverError.value = ''
  }
})

onBeforeUnmount(() => {
  authStore.clearError()
})

const onSubmit = async (values: LoginFormValues) => {
  if (!formData.username && values.username) {
    formData.username = values.username
  }
  
  if (!formData.password && values.password) {
    formData.password = values.password
  }
  
  serverError.value = ''
  isSubmitting.value = true
  
  try {
    const username = formData.username.trim()
    const password = formData.password.trim()
    
    if (!username || !password) {
      serverError.value = 'Username and password are required'
      isSubmitting.value = false
      return
    }

    const loginData = { username, password }
    document.body.style.cursor = 'wait'
    
    await authStore.login(loginData)
    
    const redirectPath = route.query.redirect as string
    if (redirectPath) {
      await router.push(redirectPath)
    } else {
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
    
    # Register View
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/views/Register.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="space-y-6">
    <Form v-slot="{ errors: formErrors, submitCount, submitForm }" class="space-y-6" @submit="handleSubmit">
      <!-- Top row - full width fields -->
      <div class="space-y-5">
        <!-- Username input -->
        <div class="relative">
          <Field name="username" rules="required|username" :validateOnBlur="false" v-slot="{ errorMessage, field }">
            <FormInput
              v-bind="field"
              name="username"
              label="Username"
              icon="fas fa-user"
              placeholder="Create a username"
              :disabled="authStore.loading || isSubmitting"
              :hasError="!!errorMessage && submitCount > 0"
              v-model="formData.username"
              class="min-h-[42px] sm:min-h-[48px] shadow-sm hover:shadow-md transition-shadow duration-300"
            />
          </Field>
        </div>

        <!-- Email input -->
        <div class="relative">
          <Field name="email" rules="required|email" :validateOnBlur="false" v-slot="{ errorMessage, field }">
            <FormInput
              v-bind="field"
              name="email"
              label="Email"
              icon="fas fa-envelope"
              placeholder="Enter your email"
              :disabled="authStore.loading || isSubmitting"
              :hasError="!!errorMessage && submitCount > 0"
              v-model="formData.email"
              class="min-h-[42px] sm:min-h-[48px] shadow-sm hover:shadow-md transition-shadow duration-300"
            />
          </Field>
        </div>
      </div>

      <!-- Password section -->
      <div class="space-y-5">
        <div class="space-y-5">
          <div class="relative">
            <Field name="password" rules="required|registration_password" :validateOnBlur="false" v-slot="{ errorMessage, field }">
              <PasswordInput
                v-bind="field"
                name="password"
                v-model="formData.password"
                placeholder="Create password"
                :disabled="authStore.loading || isSubmitting"
                :hasError="!!errorMessage && submitCount > 0"
                class="min-h-[42px] sm:min-h-[48px] shadow-sm hover:shadow-md transition-shadow duration-300"
              />
            </Field>
          </div>

          <div class="relative">
            <Field name="password_confirmation" :rules="{ required: true, password_confirmation: formData.password }" :validateOnBlur="false" v-slot="{ errorMessage, field }">
              <PasswordInput
                v-bind="field"
                name="password_confirmation"
                v-model="formData.passwordConfirmation"
                placeholder="Confirm password"
                :disabled="authStore.loading || isSubmitting"
                :hasError="!!errorMessage && submitCount > 0"
                class="min-h-[42px] sm:min-h-[48px] shadow-sm hover:shadow-md transition-shadow duration-300"
              />
            </Field>
          </div>
        </div>

        <!-- Password requirements -->
        <div class="px-5 py-4 bg-white/5 backdrop-blur-sm rounded-xl border border-white/20 hover:border-blue-400/30 transition-all duration-300 shadow-inner">
          <PasswordRequirements 
            :password="formData.password || ''"
            ref="passwordRequirements"
            class="text-sm"
          />
        </div>
      </div>

      <!-- Bottom section -->
      <div class="space-y-5 pt-3">
        <!-- Terms checkbox -->
        <Field name="agreeToTerms" rules="required|terms" :validateOnBlur="false">
          <FormCheckbox 
            name="agreeToTerms" 
            :disabled="authStore.loading || isSubmitting"
            :showError="false"
          >
            I agree to the 
            <router-link to="/terms" class="text-blue-400 hover:text-blue-300 transition-colors duration-300 font-medium underline decoration-blue-400/40">
              Terms of Service
            </router-link>
            and
            <router-link to="/privacy" class="text-blue-400 hover:text-blue-300 transition-colors duration-300 font-medium underline decoration-blue-400/40">
              Privacy Policy
            </router-link>
          </FormCheckbox>
        </Field>

        <!-- Error message -->
        <transition name="fade-up">
          <div v-if="serverError" 
               class="p-4 bg-red-500/20 border border-red-400/40 rounded-xl backdrop-blur-sm shadow-lg shadow-red-500/10">
            <p class="text-sm font-medium text-red-100 text-center whitespace-pre-line">{{ serverError }}</p>
          </div>
        </transition>

        <!-- Submit button -->
        <GradientButton
          type="submit"
          :disabled="authStore.loading || isSubmitting"
          :loading="authStore.loading || isSubmitting"
          loading-text="Creating account..."
          class="w-full min-h-[48px] sm:min-h-[52px] mt-4"
        >
          Create Account
        </GradientButton>
      </div>
    </Form>

    <!-- AuthLinks -->
    <div class="pt-4">
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Form, Field } from 'vee-validate'
import { useAuthStore } from '@/apps/auth/stores/index'
import { formatAuthError } from '@/apps/auth/plugins/validation'
import type { RegisterFormValues, PasswordRequirementsRef } from '@/apps/auth/types/form'
import { AuthAPI } from '@/apps/auth/services/api'

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

const formData = reactive({
  email: '',
  password: '',
  passwordConfirmation: '',
  username: '',
  agreeToTerms: false
})

onMounted(async () => {
  try {
    const healthResponse = await AuthAPI.healthCheck()
    console.log('Auth service health check:', healthResponse.data)
  } catch (error) {
    console.error('Auth service health check failed:', error)
  }
})

watch(
  [() => formData.email, () => formData.password, () => formData.passwordConfirmation, () => formData.username],
  () => {
    if (serverError.value) {
      serverError.value = ''
    }
  }
)

onBeforeUnmount(() => {
  authStore.clearError()
})

const handleSubmit = async (values: RegisterFormValues) => {
  serverError.value = ''
  isSubmitting.value = true

  try {
    if (!formData.username && values.username) {
      formData.username = values.username
    }
    
    if (!formData.email && values.email) {
      formData.email = values.email
    }
    
    if (!formData.password && values.password) {
      formData.password = values.password
    }
    
    if (!formData.username || !formData.email || !formData.password || !values.agreeToTerms) {
      serverError.value = 'All fields are required'
      isSubmitting.value = false
      return
    }

    if (formData.password !== formData.passwordConfirmation) {
      serverError.value = 'Passwords do not match'
      isSubmitting.value = false
      return
    }

    const registerData = {
      username: formData.username.trim(),
      email: formData.email.trim(),
      password: formData.password,
      password_confirmation: formData.passwordConfirmation,
      terms_accepted: values.agreeToTerms
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
    
    # Auth Layout
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/layouts/AuthLayout.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="w-full min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
    <!-- Background Elements -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <!-- Animated gradient mesh -->
      <div class="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10"></div>
      
      <!-- Glowing orbs -->
      <div class="absolute top-[10%] left-[5%] w-[300px] sm:w-[500px] md:w-[800px] h-[300px] sm:h-[500px] md:h-[800px] rounded-full bg-gradient-to-br from-blue-500/20 to-cyan-500/20 blur-[80px] sm:blur-[120px] animate-pulse"></div>
      <div class="absolute bottom-[20%] right-[10%] w-[200px] sm:w-[400px] md:w-[600px] h-[200px] sm:h-[400px] md:h-[600px] rounded-full bg-gradient-to-br from-purple-500/20 to-pink-500/20 blur-[60px] sm:blur-[100px] animate-pulse" style="animation-delay: 1s;"></div>
      <div class="absolute top-[50%] right-[20%] w-[250px] sm:w-[350px] h-[250px] sm:h-[350px] rounded-full bg-gradient-to-br from-violet-500/15 to-indigo-500/15 blur-[70px] animate-pulse" style="animation-delay: 2s;"></div>
      
      <!-- Grid pattern overlay -->
      <div class="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:100px_100px]"></div>
    </div>

    <!-- Content wrapper -->
    <div class="flex min-h-screen w-full">
      <div class="w-full flex items-center justify-center px-4 py-16 pt-28 sm:pt-32 relative">
        <!-- Auth Container -->
        <div class="w-full max-w-[480px] mx-auto relative z-10">
          <div class="bg-white/10 backdrop-blur-2xl rounded-3xl p-8 sm:p-10 border border-white/20 hover:border-blue-400/40 transition-all duration-500 shadow-[0_20px_80px_-20px_rgba(0,0,0,0.5)] hover:shadow-[0_20px_100px_-20px_rgba(59,130,246,0.3)]">
            <!-- Logo and Title Section -->
            <div class="text-center mb-10">
              <div class="inline-flex items-center justify-center mb-8">
                <div class="p-4 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-400/30 shadow-lg shadow-blue-500/20">
                  <h1 class="text-3xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                    {{ $route.meta.title || 'Auth' }}
                  </h1>
                </div>
              </div>
              <h2 class="text-2xl sm:text-3xl font-semibold text-white mb-3 tracking-tight">
                {{ $route.meta.title }}
              </h2>
              <p class="text-base text-blue-100/90 font-medium">
                {{ $route.meta.subtitle }}
              </p>
            </div>

            <!-- Main Content -->
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
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const $route = useRoute()
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.05);
  }
}

.animate-pulse {
  animation: pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
'''
    })
    
    # ===== Components =====
    
    # Component barrel files
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
'''
    })
    
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/organisms/index.ts',
        'type': 'typescript',
        'content': '''// Header Components
export { default as AuthHeader } from './headers/AuthHeader.vue';
'''
    })
    
    # Atom Components
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/atoms/buttons/GradientButton.vue',
        'type': 'vue',
        'content': '''<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="w-full bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 
           hover:from-blue-500 hover:via-purple-500 hover:to-pink-500 
           text-white font-semibold py-4 px-6 rounded-xl 
           transition-all duration-500 transform hover:-translate-y-1 hover:scale-[1.02] 
           flex items-center justify-center text-base disabled:opacity-50 
           disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:scale-100
           shadow-[0_10px_30px_-5px_rgba(59,130,246,0.5),0_10px_20px_-5px_rgba(168,85,247,0.4)] 
           hover:shadow-[0_20px_40px_-5px_rgba(59,130,246,0.6),0_15px_30px_-5px_rgba(168,85,247,0.5)]
           border border-white/20 hover:border-white/40
           backdrop-blur-sm relative overflow-hidden group"
  >
    <div class="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 
                translate-x-[-100%] group-hover:translate-x-[100%] 
                transition-transform duration-1000"></div>
    <span v-if="loading" class="flex items-center justify-center relative z-10">
      <i class="fas fa-circle-notch fa-spin mr-2"></i>
      <span class="font-medium">{{ loadingText }}</span>
    </span>
    <span v-else class="flex items-center justify-center space-x-2 relative z-10">
      <span class="font-medium"><slot></slot></span>
      <i class="fas fa-arrow-right transform transition-transform duration-500 
                group-hover:translate-x-1"></i>
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
'''
    })
    
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/atoms/inputs/PasswordInput.vue',
        'type': 'vue',
        'content': '''<template>
  <div>
    <label v-if="label" :for="id" class="sr-only">{{ label }}</label>
    <div class="relative group">
      <span class="absolute inset-y-0 left-0 flex items-center pl-4">
        <i class="fas fa-lock text-blue-300/60 group-hover:text-blue-400 transition-colors"></i>
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
        class="w-full py-3.5 pl-11 pr-10 bg-white/5 border rounded-xl 
               text-white placeholder-blue-200/40 outline-none focus:outline-none
               disabled:opacity-50 disabled:cursor-not-allowed 
               transition-all duration-300 backdrop-blur-sm"
        :class="{ 
          'border-red-400/50 ring-2 ring-red-400/30 focus:ring-red-400/50': hasError,
          'border-white/20 focus:border-blue-400/60 focus:ring-2 focus:ring-blue-400/30 focus:bg-white/10': !hasError,
          'hover:border-white/30 hover:bg-white/8': !hasError && !disabled
        }"
      >
      <button
        type="button"
        @click="togglePassword"
        class="absolute inset-y-0 right-0 flex items-center pr-4 text-blue-300/60 
               hover:text-blue-400 transition-colors duration-300"
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
    required: true
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
input:focus {
  outline: none !important;
  box-shadow: none !important;
}

input:focus-visible {
  outline: none !important;
}
</style>
'''
    })
    
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/atoms/items/RequirementItem.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="flex items-center gap-2">
    <i class="fas fa-check text-xs"
       :class="checked ? 'text-green-400' : 'text-blue-300/40'">
    </i>
    <span :class="[
      'text-sm transition-colors duration-200',
      checked ? 'text-blue-100' : 'text-blue-200/60'
    ]">{{ text }}</span>
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
    
    # Molecule Components
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/molecules/forms/FormInput.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="form-group">
    <label class="relative block group">
      <span class="sr-only">{{ label }}</span>
      <span class="absolute inset-y-0 left-0 flex items-center pl-4">
        <i :class="[icon, 'text-blue-300/60 group-hover:text-blue-400 transition-colors']"></i>
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
        class="w-full py-3.5 pl-11 pr-4 bg-white/5 border rounded-xl 
               text-white placeholder-blue-200/40 outline-none focus:outline-none
               disabled:opacity-50 disabled:cursor-not-allowed 
               transition-all duration-300 backdrop-blur-sm"
        :class="{ 
          'border-red-400/50 ring-2 ring-red-400/30 focus:ring-red-400/50': hasError, 
          'border-white/20 focus:border-blue-400/60 focus:ring-2 focus:ring-blue-400/30 focus:bg-white/10': !hasError,
          'hover:border-white/30 hover:bg-white/8': !hasError && !disabled
        }"
      >
    </label>
    <ErrorMessage v-if="showError" :name="name" class="mt-2 text-sm text-red-400" />
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
input:focus {
  outline: none !important;
  box-shadow: none !important;
}

input:focus-visible {
  outline: none !important;
}
</style>
'''
    })
    
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/molecules/forms/FormCheckbox.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="flex items-start p-4 rounded-xl bg-white/5 border border-white/20 
              hover:border-blue-400/40 transition-all duration-300 backdrop-blur-sm">
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
          class="w-4 h-4 border border-white/30 rounded bg-white/10 text-blue-500 
                 focus:ring-blue-400/50 focus:ring-offset-0 focus:ring-2
                 disabled:opacity-50 disabled:cursor-not-allowed
                 transition-all duration-300"
        >
      </Field>
    </div>
    <div class="ml-3">
      <label class="text-sm text-blue-100">
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
    <div class="grid grid-cols-2 gap-x-8 gap-y-2">
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
  <div class="mt-6 sm:mt-8 space-y-4 sm:space-y-6">
    <!-- Divider -->
    <div class="relative">
      <div class="absolute inset-0 flex items-center">
        <div class="w-full h-px bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>
      </div>
      <div class="relative flex justify-center text-sm">
        <span class="px-4 bg-white/10 backdrop-blur-sm text-blue-200 rounded-full border border-white/20">or</span>
      </div>
    </div>

    <!-- Links Section -->
    <div class="text-center space-y-5 sm:space-y-6">
      <div class="transform hover:scale-[1.01] transition-all duration-300">
        <p class="text-blue-100 text-sm sm:text-base">
          <template v-if="isLoginPage">
            New here?
            <router-link 
              to="/auth/register" 
              class="text-blue-400 hover:text-blue-300 font-medium transition-colors duration-300 underline decoration-blue-400/40 hover:decoration-blue-300/60"
            >
              Create an account
            </router-link>
          </template>
          <template v-else>
            Already have an account?
            <router-link 
              to="/auth/signin" 
              class="text-blue-400 hover:text-blue-300 font-medium transition-colors duration-300 underline decoration-blue-400/40 hover:decoration-blue-300/60"
            >
              Sign in here
            </router-link>
          </template>
        </p>
      </div>

      <!-- Home Link -->
      <router-link 
        to="/" 
        class="inline-flex items-center gap-2 px-4 sm:px-5 py-2.5 sm:py-3 rounded-xl text-blue-200 
               hover:text-white transition-all duration-300 group hover:bg-white/10
               text-sm sm:text-base backdrop-blur-sm border border-white/20
               hover:border-blue-400/40 transform hover:-translate-y-1"
      >
        <i class="fas fa-arrow-left text-xs sm:text-sm transform group-hover:-translate-x-1.5 transition-transform duration-500"></i>
        Back to Home
      </router-link>
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
    
    # Organism Components
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
    
    # Create API directory structure
    files.append({
        'name': 'backend/django/apps/auth/__init__.py',
        'type': 'python',
        'content': ''
    })
    
    files.append({
        'name': 'backend/django/apps/auth/api/__init__.py',
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
'''
    })
    
    files.append({
        'name': 'backend/django/apps/auth/models.py',
        'type': 'python',
        'content': '''from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.user.username}'s profile (${self.balance:.2f})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, balance=0.00)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance, balance=0.00)
    instance.profile.save()
'''
    })
    
    files.append({
        'name': 'backend/django/apps/auth/api/serializers.py',
        'type': 'python',
        'content': '''from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(source='profile.balance', max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'balance')
        read_only_fields = ('id', 'balance')

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)

    def validate_username(self, username):
        username = username.strip()
        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError(
                "This username is already taken. Please choose another one."
            )
        return username

    def validate_email(self, email):
        email = email.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "A user is already registered with this e-mail address."
            )
        return email

    def validate_password(self, password):
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        return password

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError({"password_confirmation": "Passwords don't match"})
        return data

    def save(self):
        user = User.objects.create_user(
            username=self.validated_data['username'],
            email=self.validated_data['email'],
            password=self.validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username', '').strip()
        password = attrs.get('password', '')
        
        if not username:
            raise serializers.ValidationError({
                'username': 'Username is required'
            })
        
        if not password:
            raise serializers.ValidationError({
                'password': 'Password is required'
            })
        
        try:
            user_exists = User.objects.filter(username__iexact=username).exists()
            if not user_exists:
                raise serializers.ValidationError({
                    'error': 'No account found with this username'
                })
            
            user = authenticate(
                username=username,
                password=password
            )

            if not user:
                raise serializers.ValidationError({
                    'error': 'Invalid password. Please try again'
                })

            if not user.is_active:
                raise serializers.ValidationError({
                    'error': 'This account has been disabled'
                })

            attrs['user'] = user
            return attrs

        except serializers.ValidationError:
            raise
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Login validation error: {str(e)}")
            raise serializers.ValidationError({
                'error': 'Login failed. Please try again later'
            })
'''
    })
    
    files.append({
        'name': 'backend/django/apps/auth/api/views.py',
        'type': 'python',
        'content': '''from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import get_user_model, login
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class CSRFTokenView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        csrf_token = get_token(request)
        return Response({'csrfToken': csrf_token, 'details': 'CSRF cookie set'}, status=200)

class InitView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]
    
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        is_authenticated = request.user.is_authenticated
        return Response({
            'isAuthenticated': is_authenticated,
            'user': UserSerializer(request.user).data if is_authenticated else None,
            'csrfToken': get_token(request)
        })

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        logger.info(f"Registration attempt from {request.META.get('REMOTE_ADDR')}")
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response({
                'error': 'Registration failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            login(request, user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response({
                'error': 'Login failed',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            if request.user.is_authenticated:
                request.user.auth_token.delete()
            return Response({'message': 'Logout successful'})
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response({
                'error': 'Logout failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        try:
            User.objects.exists()
            
            return Response({
                'status': 'healthy',
                'service': 'auth',
                'database': 'connected'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return Response({
                'status': 'unhealthy',
                'service': 'auth',
                'error': str(e),
                'database': 'disconnected'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
'''
    })
    
    files.append({
        'name': 'backend/django/apps/auth/api/urls.py',
        'type': 'python',
        'content': '''from django.urls import path
from . import views

app_name = 'auth_api'

urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path('csrf/', views.CSRFTokenView.as_view(), name='csrf-token'),
    path('init/', views.InitView.as_view(), name='init'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('user/', views.UserView.as_view(), name='user'),
]
'''
    })
    
    files.append({
        'name': 'backend/django/apps/auth/admin.py',
        'type': 'python',
        'content': '''from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance']
    list_filter = ['balance']
    search_fields = ['user__username', 'user__email']
'''
    })
    
    files.append({
        'name': 'backend/django/apps/auth/tests.py',
        'type': 'python',
        'content': '''from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTestCase(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertEqual(user.username, 'testuser')
'''
    })
    
    return files


def payments_app_files() -> List[Dict[str, str]]:
    app_name = 'payments'
    cap = 'Payments'
    welcome = 'Manage subscriptions and transactions.'
    files: List[Dict[str, str]] = []
    files += _frontend_scaffold(app_name, cap, welcome)
    files += _backend_scaffold(app_name, cap)

    # Minimal payments-specific backend endpoints
    files.append({
        'name': f'backend/django/apps/{app_name}/views.py',
        'type': 'python',
        'content': (
            "from rest_framework.decorators import api_view\n"
            "from rest_framework.response import Response\n"
            "from rest_framework import status\n\n"
            "@api_view(['GET'])\n"
            "def plans(_request):\n"
            "    return Response({'plans': []}, status=status.HTTP_200_OK)\n\n"
            "@api_view(['POST'])\n"
            "def checkout(_request):\n"
            "    return Response({'status': 'not implemented'}, status=status.HTTP_200_OK)\n"
        ),
    })
    files.append({
        'name': f'backend/django/apps/{app_name}/urls.py',
        'type': 'python',
        'content': (
            "from django.urls import path\n"
            "from . import views\n\n"
            "urlpatterns = [\n"
            "    path('plans/', views.plans, name='plans'),\n"
            "    path('checkout/', views.checkout, name='checkout'),\n"
            "]\n"
        ),
    })
    return files


PREBUILT_MAP = {
    'home': home_app_files,
    'auth': auth_app_files,
    'payments': payments_app_files,
}


def generate_prebuilt_app_files(app_name: str, app_description: str | None = None) -> List[Dict[str, str]]:
    key = (app_name or '').lower()
    func = PREBUILT_MAP.get(key)
    if not func:
        return []
    return func()
