import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { AuthAPI } from '../services/api'
import { useAuthStore as useGlobalAuthStore } from '@/shared/stores/auth'
import type { LoginCredentials, AuthResponse, UserRegistrationData } from '../types/auth'

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

    let serverLogoutFailed = false

    try {
      isLoggingOut.value = true
      lastAuthAction.value = 'logout'

      if (globalAuthStore.isAuthenticated) {
        await AuthAPI.logout()
      }
    } catch (err) {
      // The server-side token deletion did not happen, so the token may still
      // be valid. Recorded rather than swallowed: the local teardown below
      // runs either way, but the user needs to know the session may live on.
      serverLogoutFailed = true
      console.error('Sign-out request failed; clearing this browser anyway', err)
    } finally {
      // Unconditional: a failed request must never leave the browser holding a
      // live token. Signing out on a shared machine and staying signed in is
      // the failure this ordering exists to prevent.
      try {
        await globalAuthStore.clearAuth()
        if (router) {
          await router.push('/')
        }
      } finally {
        isLoggingOut.value = false
      }
    }

    if (serverLogoutFailed) {
      throw new Error(
        'You have been signed out on this device, but the server could not be reached. ' +
        'If you are on a shared computer, sign in again and sign out to fully revoke access.'
      )
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
    initAuth,
    clearError
  }
})
