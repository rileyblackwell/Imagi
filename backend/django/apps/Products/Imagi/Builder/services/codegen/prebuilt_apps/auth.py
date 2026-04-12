"""
Auth app prebuilt template.
Generates comprehensive authentication app files with full Login/Register functionality.
Self-contained auth app mirroring the Imagi design with dark/light mode support.
No external dependencies - everything is contained within this app.
"""
from __future__ import annotations

from typing import Dict, List


def auth_app_files() -> List[Dict[str, str]]:
    """
    Generate comprehensive authentication app files with full Login/Register functionality.
    Self-contained auth app mirroring the Imagi design with dark/light mode support.
    No external dependencies - everything is contained within this app.
    """
    files: List[Dict[str, str]] = []
    
    # ========== Frontend Files ==========
    
    # Main index.ts
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/index.ts',
        'type': 'typescript',
        'content': '''export { useAuthStore } from './stores/auth'
export type { User, AuthState, LoginCredentials, UserRegistrationData, AuthResponse } from './types/auth'
'''
    })
    
    # ===== Types =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/types/auth.ts',
        'type': 'typescript',
        'content': '''export interface User {
  id: number;
  email: string;
  username: string;
  name?: string;
  balance?: number;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface UserRegistrationData {
  username: string;
  email: string;
  password: string;
  password_confirmation: string;
  terms_accepted?: boolean;
}

export interface AuthResponse {
  token: string;
  user: User;
}
'''
    })
    
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/types/form.ts',
        'type': 'typescript',
        'content': '''export interface RegisterFormValues {
  username?: string;
  email?: string;
  password?: string;
  password_confirmation?: string;
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
    
    # ===== Validation Plugin =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/plugins/validation.ts',
        'type': 'typescript',
        'content': '''import { configure, defineRule } from 'vee-validate'
import type { App } from 'vue'

// Define base rules
defineRule('required', () => true)
defineRule('email', (value: string) => {
  if (value && !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(value)) {
    return 'Please enter a valid email address'
  }
  return true
})

// Username validation
defineRule('username', (value: string) => {
  if (!value) return true
  if (value.length < 3) return 'Username must be at least 3 characters'
  if (value.length > 150) return 'Username must be less than 150 characters'
  if (!/^[a-zA-Z0-9_]+$/.test(value)) return 'Username can only contain letters, numbers, and underscores'
  return true
})

defineRule('terms', () => true)

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

defineRule('login_username', () => true)
defineRule('login_password', () => true)

const errorMessages = {
  'This username is already taken. Please choose another one.': 'This username is already taken. Please try another one.',
  'A user is already registered with this e-mail address.': 'This email is already registered. Please use another one or sign in.',
  'No account found with this username': 'No account found with this username. Please check your spelling or create an account.',
  'Invalid password. Please try again': 'Incorrect password. Please try again.',
  'This account has been disabled': 'This account has been disabled. Please contact support.',
  'Unable to log in with provided credentials.': 'Invalid username or password. Please try again.',
  'Network Error': 'Unable to connect to server. Please check your internet connection.',
  'Network Error: Unable to connect to server': 'Unable to reach the server. Please check your connection.',
  'default': 'An unexpected error occurred. Please try again.'
} as const

export const formatAuthError = (error: unknown, context: 'login' | 'register' = 'login'): string => {
  if (!error) return errorMessages.default
  
  if (error instanceof Error) {
    const message = error.message
    const axiosError = error as any
    
    if (axiosError?.response?.data) {
      const responseData = axiosError.response.data
      if (responseData.error) {
        return errorMessages[responseData.error as keyof typeof errorMessages] || responseData.error
      }
      if (responseData.detail) {
        if (typeof responseData.detail === 'object') {
          const fieldMessages = []
          for (const [field, msg] of Object.entries(responseData.detail)) {
            const normalizedMessage = Array.isArray(msg) ? msg[0] : msg
            if (field === 'non_field_errors' || field === 'error') {
              fieldMessages.push(normalizedMessage)
            } else {
              fieldMessages.push(`${field}: ${normalizedMessage}`)
            }
          }
          return fieldMessages.join('\\n')
        }
        return responseData.detail
      }
      if (responseData.non_field_errors && Array.isArray(responseData.non_field_errors)) {
        return responseData.non_field_errors[0]
      }
    }
    
    const formattedMessage = errorMessages[message as keyof typeof errorMessages]
    return formattedMessage || message
  }
  
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
    
    # ===== Self-contained API Service =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/services/api.ts',
        'type': 'typescript',
        'content': '''import axios from 'axios'
import type { User, LoginCredentials, AuthResponse, UserRegistrationData } from '../types/auth'

// Create self-contained axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

const API_PATH = '/v1/auth'

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
    return await api.get(`${API_PATH}/csrf/`)
  },

  async ensureCSRFToken(): Promise<string | null> {
    let csrfToken = getCookie('csrftoken')
    if (!csrfToken) {
      await this.getCSRFToken()
      csrfToken = getCookie('csrftoken')
    }
    return csrfToken
  },

  async login(credentials: LoginCredentials): Promise<{ data: AuthResponse }> {
    if (!credentials?.username || !credentials?.password) {
      throw new Error('Username and password are required')
    }

    const csrfToken = await this.ensureCSRFToken()
    const response = await api.post(`${API_PATH}/signin/`, credentials, {
      headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {},
    })

    if (!response.data?.token && !response.data?.key) {
      throw new Error('Invalid server response')
    }

    return { 
      data: {
        token: response.data.token || response.data.key,
        user: response.data.user || {}
      }
    }
  },

  async register(userData: UserRegistrationData): Promise<{ data: AuthResponse }> {
    const csrfToken = await this.ensureCSRFToken()
    
    const response = await api.post(`${API_PATH}/register/`, {
      username: userData.username,
      email: userData.email,
      password: userData.password,
      password_confirmation: userData.password_confirmation
    }, {
      headers: csrfToken ? { 'X-CSRFToken': csrfToken } : {},
    })
    
    return { 
      data: {
        token: response.data.token || response.data.key,
        user: response.data.user || {}
      }
    }
  },

  async logout(): Promise<void> {
    if (logoutPromise) return logoutPromise
    try {
      logoutPromise = api.post(`${API_PATH}/logout/`, {})
      await logoutPromise
      localStorage.removeItem('token')
    } finally {
      logoutPromise = null
    }
  },

  async healthCheck(): Promise<{ data: { status: string } }> {
    return await api.get(`${API_PATH}/health/`)
  }
}
'''
    })
    
    # ===== Self-contained Auth Store =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/stores/auth.ts',
        'type': 'typescript',
        'content': '''import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { AuthAPI } from '../services/api'
import type { LoginCredentials, AuthResponse, UserRegistrationData, User } from '../types/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isLoggingOut = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  const setAuthState = (newUser: User | null, newToken: string | null) => {
    user.value = newUser
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
    } else {
      localStorage.removeItem('token')
    }
  }

  const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
    loading.value = true
    error.value = null
    try {
      const response = await AuthAPI.login(credentials)
      setAuthState(response.data.user, response.data.token)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const register = async (userData: UserRegistrationData): Promise<AuthResponse> => {
    loading.value = true
    error.value = null
    try {
      const response = await AuthAPI.register(userData)
      setAuthState(response.data.user, response.data.token)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = async (router?: any): Promise<void> => {
    if (isLoggingOut.value) return
    try {
      isLoggingOut.value = true
      await AuthAPI.logout()
    } finally {
      setAuthState(null, null)
      isLoggingOut.value = false
      if (router) {
        await router.push('/')
      }
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    user,
    token,
    loading,
    error,
    isLoggingOut,
    isAuthenticated,
    login,
    register,
    logout,
    clearError,
    setAuthState
  }
})
'''
    })
    
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/stores/index.ts',
        'type': 'typescript',
        'content': '''export { useAuthStore } from './auth'
'''
    })
    
    # ===== Router =====
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
          title: 'Welcome Back',
          subtitle: 'Sign in to continue building amazing applications'
        }
      },
      {
        path: 'register',
        name: 'register',
        component: () => import('../views/Register.vue'),
        meta: {
          requiresAuth: false,
          title: 'Create Account',
          subtitle: 'Start building your next great idea'
        }
      }
    ]
  }
]

export { routes }
export default routes
'''
    })
    
    # ===== Self-contained AuthLayout =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/layouts/AuthLayout.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="min-h-screen bg-gray-50 dark:bg-[#0f0f0f] relative overflow-hidden transition-colors duration-500">
    <!-- Background -->
    <div class="fixed inset-0 pointer-events-none">
      <div class="absolute inset-0 bg-gradient-to-b from-gray-50/50 via-gray-50 to-gray-50 dark:from-[#0f0f0f] dark:via-[#0f0f0f] dark:to-[#0f0f0f] transition-colors duration-500"></div>
      <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]" 
           style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
    </div>

    <!-- Content -->
    <div class="flex min-h-screen w-full relative z-10">
      <div class="w-full flex items-center justify-center px-4 sm:px-6 py-16 pt-28 sm:pt-32">
        <div class="w-full max-w-[520px] mx-auto">
          <div class="relative animate-fade-in">
            <div class="relative rounded-2xl border border-gray-200/80 dark:border-white/[0.08] bg-white dark:bg-[#0a0a0f]/50 shadow-sm dark:shadow-none backdrop-blur-xl overflow-hidden transition-all duration-300">
              <div class="relative z-10 p-8 sm:p-10">
                <!-- Logo and Title -->
                <div class="text-center mb-10">
                  <div class="inline-flex items-center justify-center mb-8">
                    <router-link to="/" class="text-3xl font-bold text-black dark:text-white">
                      App
                    </router-link>
                  </div>
                  <h2 class="text-xl sm:text-2xl font-medium tracking-tight mb-3 text-black dark:text-white transition-colors duration-300">
                    {{ $route.meta.title }}
                  </h2>
                  <p class="text-base text-gray-500 dark:text-white/80 leading-relaxed transition-colors duration-300">
                    {{ $route.meta.subtitle }}
                  </p>
                </div>

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
    
    # ===== Views =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/views/index.ts',
        'type': 'typescript',
        'content': '''export { default as Login } from './Login.vue'
export { default as Register } from './Register.vue'
'''
    })
    
    # Login View - matching Imagi design
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/views/Login.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="space-y-6">
    <Form v-slot="{ errors: formErrors, submitCount }" class="space-y-5" @submit="onSubmit">
      <!-- Username input -->
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

      <!-- Password input -->
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

      <!-- Error message -->
      <div class="space-y-5 pt-2">
        <transition name="fade-up">
          <div v-if="serverError" 
               class="p-4 rounded-xl border border-red-500/20 bg-red-50 dark:bg-red-500/10 backdrop-blur-sm transition-colors duration-300">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-500/20 border border-red-200 dark:border-red-500/30 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-exclamation-triangle text-red-600 dark:text-red-400 text-sm"></i>
              </div>
              <p class="text-sm font-medium text-red-600 dark:text-red-400 whitespace-pre-line">
                {{ serverError }}
              </p>
            </div>
          </div>
        </transition>

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

    <!-- Separator -->
    <div class="relative py-4">
      <div class="relative flex items-center justify-center">
        <div class="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300/50 dark:via-white/[0.08] to-transparent"></div>
        <div class="mx-4 text-xs text-gray-400 dark:text-white uppercase tracking-wider">or</div>
        <div class="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300/50 dark:via-white/[0.08] to-transparent"></div>
      </div>
    </div>

    <!-- Register link -->
    <div class="text-center">
      <p class="text-black dark:text-white text-sm">
        New here?
        <router-link to="/auth/register" class="text-black dark:text-white font-medium ml-1">
          Create an account
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Form, Field } from 'vee-validate'
import { useAuthStore } from '../stores/auth'
import { formatAuthError } from '../plugins/validation'
import type { LoginFormValues } from '../types/form'
import FormInput from '../components/molecules/forms/FormInput.vue'
import PasswordInput from '../components/atoms/inputs/PasswordInput.vue'
import GradientButton from '../components/atoms/buttons/GradientButton.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const serverError = ref('')
const isSubmitting = ref(false)

onBeforeUnmount(() => {
  authStore.clearError()
})

const onSubmit = async (values: LoginFormValues) => {
  serverError.value = ''
  isSubmitting.value = true
  
  try {
    const username = values.username?.trim()
    const password = values.password?.trim()
    
    if (!username || !password) {
      serverError.value = 'Username and password are required'
      isSubmitting.value = false
      return
    }

    await authStore.login({ username, password })
    
    const redirectPath = route.query.redirect as string
    await router.push(redirectPath || '/')
  } catch (error: unknown) {
    serverError.value = formatAuthError(error, 'login')
  } finally {
    isSubmitting.value = false
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
    
    # Register View - matching Imagi design
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/views/Register.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="space-y-6">
    <Form v-slot="{ errors: formErrors, submitCount: formSubmitCount }" class="space-y-5" @submit="handleSubmit">
      <!-- Username input -->
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

      <!-- Email input -->
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
            <!-- Password requirements -->
            <div class="mt-4 p-4 rounded-xl border border-black/[0.08] dark:border-white/[0.08] bg-black/[0.02] dark:bg-white/[0.02] backdrop-blur-sm">
              <PasswordRequirements :password="value || ''" />
            </div>
          </Field>
        </div>

        <!-- Confirm password -->
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
        <!-- Terms checkbox -->
        <div class="p-4 rounded-xl border border-black/[0.08] dark:border-white/[0.08] bg-black/[0.02] dark:bg-white/[0.02] backdrop-blur-sm hover:bg-black/[0.04] dark:hover:bg-white/[0.04] transition-all duration-300">
          <Field name="agreeToTerms" :rules="{ required: { allowFalse: false } }" :validateOnBlur="false" v-slot="{ errorMessage }">
            <FormCheckbox name="agreeToTerms" :disabled="authStore.loading || isSubmitting">
              I agree to the 
              <router-link to="/terms" class="text-black dark:text-white hover:text-black/70 dark:hover:text-white/70 font-medium">Terms of Service</router-link>
              and
              <router-link to="/privacy" class="text-black dark:text-white hover:text-black/70 dark:hover:text-white/70 font-medium">Privacy Policy</router-link>
            </FormCheckbox>
            <div v-if="(errorMessage || !hasAcceptedTerms) && formSubmitCount > 0" class="mt-2 text-sm text-red-400 flex items-center gap-2">
              <i class="fas fa-exclamation-circle text-xs"></i>
              <span>You must accept the terms to continue</span>
            </div>
          </Field>
        </div>

        <!-- Error message -->
        <transition name="fade-up">
          <div v-if="serverError" class="p-4 rounded-xl border border-red-500/20 bg-red-500/10 backdrop-blur-sm">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-red-500/20 border border-red-500/30 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-exclamation-triangle text-red-400 text-sm"></i>
              </div>
              <p class="text-sm font-medium text-red-400 whitespace-pre-line">{{ serverError }}</p>
            </div>
          </div>
        </transition>

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

    <!-- Separator -->
    <div class="relative py-4">
      <div class="relative flex items-center justify-center">
        <div class="flex-1 h-px bg-gradient-to-r from-transparent via-black/[0.08] dark:via-white/[0.08] to-transparent"></div>
        <div class="mx-4 text-xs text-gray-400 dark:text-white uppercase tracking-wider">or</div>
        <div class="flex-1 h-px bg-gradient-to-r from-transparent via-black/[0.08] dark:via-white/[0.08] to-transparent"></div>
      </div>
    </div>

    <!-- Sign in link -->
    <div class="text-center">
      <p class="text-black dark:text-white text-sm">
        Already have an account?
        <router-link to="/auth/signin" class="text-black dark:text-white hover:text-gray-600 dark:hover:text-white/70 font-medium ml-1">
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
import { useAuthStore } from '../stores/auth'
import { formatAuthError } from '../plugins/validation'
import type { RegisterFormValues } from '../types/form'
import FormInput from '../components/molecules/forms/FormInput.vue'
import FormCheckbox from '../components/molecules/forms/FormCheckbox.vue'
import PasswordInput from '../components/atoms/inputs/PasswordInput.vue'
import PasswordRequirements from '../components/molecules/messages/PasswordRequirements.vue'
import GradientButton from '../components/atoms/buttons/GradientButton.vue'

const router = useRouter()
const authStore = useAuthStore()
const serverError = ref('')
const isSubmitting = ref(false)
const hasAcceptedTerms = ref(false)

onBeforeUnmount(() => {
  authStore.clearError()
})

const handleSubmit = async (values: RegisterFormValues) => {
  serverError.value = ''
  isSubmitting.value = true

  try {
    const username = values.username?.trim()
    const email = values.email?.trim()
    const password = values.password
    const passwordConfirmation = values.password_confirmation
    const agreeToTerms = values.agreeToTerms === true
    
    hasAcceptedTerms.value = agreeToTerms
    
    if (!username || !email || !password) {
      serverError.value = 'Please fill in all required fields'
      isSubmitting.value = false
      return
    }
    
    if (!agreeToTerms) {
      serverError.value = 'You must accept the Terms of Service and Privacy Policy'
      isSubmitting.value = false
      return
    }

    if (password !== passwordConfirmation) {
      serverError.value = 'Passwords do not match'
      isSubmitting.value = false
      return
    }
    
    if (password.length < 8) {
      serverError.value = 'Password must be at least 8 characters long'
      isSubmitting.value = false
      return
    }

    await authStore.register({
      username,
      email,
      password,
      password_confirmation: passwordConfirmation!,
      terms_accepted: agreeToTerms
    })
    
    await router.push('/')
  } catch (error: unknown) {
    serverError.value = formatAuthError(error, 'register')
  } finally {
    isSubmitting.value = false
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
    
    # ===== Components =====
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/index.ts',
        'type': 'typescript',
        'content': '''export * from './atoms'
export * from './molecules'
'''
    })
    
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/atoms/index.ts',
        'type': 'typescript',
        'content': '''export { default as PasswordInput } from './inputs/PasswordInput.vue'
export { default as GradientButton } from './buttons/GradientButton.vue'
export { default as RequirementItem } from './items/RequirementItem.vue'
'''
    })
    
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/molecules/index.ts',
        'type': 'typescript',
        'content': '''export { default as FormInput } from './forms/FormInput.vue'
export { default as FormCheckbox } from './forms/FormCheckbox.vue'
export { default as PasswordRequirements } from './messages/PasswordRequirements.vue'
'''
    })
    
    # Atom Components
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/atoms/inputs/PasswordInput.vue',
        'type': 'vue',
        'content': '''<template>
  <div>
    <label v-if="label" :for="id" class="sr-only">{{ label }}</label>
    <div class="relative group">
      <span class="absolute inset-y-0 left-0 flex items-center pl-4 z-10">
        <i class="fas fa-lock text-black dark:text-white transition-colors duration-200"></i>
      </span>
      <input
        :id="id"
        :value="modelValue"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @blur="onBlur"
        @change="onChange"
        :type="inputType"
        :name="name"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        class="w-full py-4 pl-12 pr-12 rounded-xl 
               text-black dark:text-white 
               placeholder-gray-400 dark:placeholder-white/30 
               outline-none focus:outline-none
               disabled:opacity-50 disabled:cursor-not-allowed 
               transition-all duration-200
               border bg-gray-50 dark:bg-white/[0.03] backdrop-blur-sm
               focus:ring-0"
        :class="{ 
          'border-red-500/50 bg-red-50 dark:bg-red-500/5': hasError,
          'border-gray-200 dark:border-white/[0.08]': !hasError
        }"
      >
      <button
        type="button"
        @click="togglePassword"
        class="absolute inset-y-0 right-0 flex items-center pr-4 
               text-black dark:text-white 
               hover:text-black/70 dark:hover:text-white/80 
               transition-colors duration-200 z-10"
      >
        <i :class="['fas', isVisible ? 'fa-eye-slash' : 'fa-eye']"></i>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const isVisible = ref(false)
const togglePassword = () => { isVisible.value = !isVisible.value }
const inputType = computed(() => isVisible.value ? 'text' : 'password')

defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  required: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  id: { type: String, default: () => `password-${Math.random().toString(36).substr(2, 9)}` },
  hasError: { type: Boolean, default: false },
  name: { type: String, default: 'password' },
  onBlur: { type: Function, default: () => {} },
  onChange: { type: Function, default: () => {} }
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
input, input:focus { outline: none !important; box-shadow: none !important; }
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
    class="group relative w-full inline-flex items-center justify-center gap-2 px-8 py-4 
           bg-black dark:bg-white 
           rounded-xl 
           text-white dark:text-gray-900 
           font-medium 
           shadow-sm 
           transition-all duration-200
           disabled:opacity-50 disabled:cursor-not-allowed
           overflow-hidden"
  >
    <span v-if="loading" class="relative z-10 flex items-center justify-center">
      <i class="fas fa-circle-notch fa-spin mr-2"></i>
      <span class="font-medium">{{ loadingText }}</span>
    </span>
    <span v-else class="relative z-10 flex items-center justify-center gap-2">
      <span class="font-medium"><slot></slot></span>
      <i class="fas fa-arrow-right text-sm"></i>
    </span>
  </button>
</template>

<script setup lang="ts">
defineProps({
  type: { type: String, default: 'button' },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  loadingText: { type: String, default: 'Loading...' }
})
</script>
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
        : 'bg-black/[0.03] dark:bg-white/[0.03] border border-black/[0.08] dark:border-white/[0.08]'"
    >
      <i 
        class="fas text-[10px] transition-all duration-300"
        :class="checked 
          ? 'fa-check text-emerald-500 dark:text-emerald-400' 
          : 'fa-circle text-black/20 dark:text-white/20'"
      ></i>
    </div>
    <span 
      class="text-sm transition-colors duration-300"
      :class="checked ? 'text-black/80 dark:text-white/80' : 'text-black/40 dark:text-white/40'"
    >
      {{ text }}
    </span>
  </div>
</template>

<script setup lang="ts">
defineProps({
  checked: { type: Boolean, default: false },
  text: { type: String, required: true }
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
      <span class="absolute inset-y-0 left-0 flex items-center pl-4 z-10">
        <i :class="[icon, 'text-black dark:text-white transition-colors duration-200']"></i>
      </span>
      <input
        :value="modelValue"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @blur="onBlur"
        @change="onChange"
        :name="name"
        :type="type"
        :disabled="disabled"
        :placeholder="placeholder"
        class="w-full py-4 pl-12 pr-4 rounded-xl 
               text-black dark:text-white 
               placeholder-gray-400 dark:placeholder-white/30 
               outline-none focus:outline-none
               disabled:opacity-50 disabled:cursor-not-allowed 
               transition-all duration-200
               border bg-gray-50 dark:bg-white/[0.03] backdrop-blur-sm
               focus:ring-0"
        :class="{ 
          'border-red-500/50 bg-red-50 dark:bg-red-500/5': hasError, 
          'border-gray-200 dark:border-white/[0.08]': !hasError
        }"
      >
    </label>
  </div>
</template>

<script setup lang="ts">
defineProps({
  modelValue: { type: String, default: '' },
  name: { type: String, required: true },
  label: { type: String, required: true },
  type: { type: String, default: 'text' },
  icon: { type: String, required: true },
  disabled: { type: Boolean, default: false },
  placeholder: { type: String, default: '' },
  hasError: { type: Boolean, default: false },
  onBlur: { type: Function, default: () => {} },
  onChange: { type: Function, default: () => {} }
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
input, input:focus { outline: none !important; box-shadow: none !important; }
</style>
'''
    })
    
    files.append({
        'name': 'frontend/vuejs/src/apps/auth/components/molecules/forms/FormCheckbox.vue',
        'type': 'vue',
        'content': '''<template>
  <div class="flex items-start">
    <div class="flex items-center h-5">
      <Field :name="name" type="checkbox" :value="true" v-slot="{ field }">
        <input
          type="checkbox"
          v-bind="field"
          :disabled="disabled"
          class="w-4 h-4 rounded 
                 border-black/20 dark:border-white/20 
                 bg-black/[0.05] dark:bg-white/[0.05] 
                 text-violet-500 focus:ring-violet-500/50 focus:ring-offset-0 focus:ring-2
                 disabled:opacity-50 disabled:cursor-not-allowed
                 transition-all duration-300
                 checked:bg-violet-500 checked:border-violet-500"
        >
      </Field>
    </div>
    <div class="ml-3">
      <label class="text-sm text-black/60 dark:text-white/60 leading-relaxed">
        <slot></slot>
      </label>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Field } from 'vee-validate'

defineProps({
  name: { type: String, required: true },
  disabled: { type: Boolean, default: false }
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
        <RequirementItem :checked="hasMinLength" text="8+ characters" />
        <RequirementItem :checked="hasUpperCase" text="One uppercase" />
        <RequirementItem :checked="hasLowerCase" text="One lowercase" />
      </div>
      <div class="space-y-2">
        <RequirementItem :checked="hasNumber" text="One number" />
        <RequirementItem :checked="hasSpecialChar" text="One symbol" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import RequirementItem from '../../atoms/items/RequirementItem.vue'

const props = defineProps({
  password: { type: String, required: true, default: '' }
})

const hasMinLength = computed(() => (props.password || '').length >= 8)
const hasUpperCase = computed(() => /[A-Z]/.test(props.password || ''))
const hasLowerCase = computed(() => /[a-z]/.test(props.password || ''))
const hasNumber = computed(() => /\\d/.test(props.password || ''))
const hasSpecialChar = computed(() => /[!@#$%^&*(),.?":{}|<>]/.test(props.password || ''))

const isValid = computed(() => 
  hasMinLength.value && hasUpperCase.value && hasLowerCase.value && hasNumber.value && hasSpecialChar.value
)

defineExpose({ isValid })
</script>
'''
    })
    
    # ========== Backend Files ==========
    
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
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
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
        fields = ('id', 'username', 'email', 'balance')
        read_only_fields = ('id', 'balance')

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)

    def validate_username(self, username):
        if User.objects.filter(username__iexact=username.strip()).exists():
            raise serializers.ValidationError("This username is already taken.")
        return username.strip()

    def validate_email(self, email):
        if User.objects.filter(email__iexact=email.strip().lower()).exists():
            raise serializers.ValidationError("This email is already registered.")
        return email.strip().lower()

    def validate_password(self, password):
        if len(password) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters.")
        return password

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError({"password_confirmation": "Passwords don't match"})
        return data

    def save(self, request=None):
        return User.objects.create_user(
            username=self.validated_data['username'],
            email=self.validated_data['email'],
            password=self.validated_data['password']
        )

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username', '').strip()
        password = attrs.get('password', '')
        
        if not username or not password:
            raise serializers.ValidationError({'error': 'Username and password are required'})
        
        if not User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError({'error': 'No account found with this username'})
        
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError({'error': 'Invalid password. Please try again'})
        if not user.is_active:
            raise serializers.ValidationError({'error': 'This account has been disabled'})

        attrs['user'] = user
        return attrs
'''
    })
    
    files.append({
        'name': 'backend/django/apps/auth/api/views.py',
        'type': 'python',
        'content': '''from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, login, logout
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
        return Response({'csrfToken': get_token(request)})

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        login(request, user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        login(request, user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response({'message': 'Logged out'})

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
        return Response({'status': 'healthy', 'service': 'auth'})
'''
    })
    
    files.append({
        'name': 'backend/django/apps/auth/api/urls.py',
        'type': 'python',
        'content': '''from django.urls import path
from . import views

app_name = 'auth_api'

urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health'),
    path('csrf/', views.CSRFTokenView.as_view(), name='csrf'),
    path('signin/', views.LoginView.as_view(), name='signin'),
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
        user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
        self.assertTrue(user.is_active)
'''
    })
    
    return files
