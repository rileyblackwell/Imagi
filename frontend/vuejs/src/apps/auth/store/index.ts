import { defineStore } from 'pinia'
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
      console.error('Registration error:', errorMessage)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Logout user
   * Handles local loading state and delegates to global auth store
   */
  const logout = async (): Promise<void> => {
    if (isLoggingOut.value) return

    try {
      isLoggingOut.value = true
      lastAuthAction.value = 'logout'
      
      if (globalAuthStore.isAuthenticated) {
        await AuthAPI.logout()
      }
      
      // Clear global auth state
      await globalAuthStore.clearAuth()
      
      // Redirect to home page
      window.location.href = '/'
    } catch (err) {
      console.error('Logout error:', err)
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
