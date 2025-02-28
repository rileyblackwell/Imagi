import { defineStore } from 'pinia'
import { ref } from 'vue'
import { AuthAPI } from '../services/api'
import { useAuthStore as useGlobalAuthStore } from '@/stores/auth'
import type { LoginCredentials, AuthResponse, UserRegistrationData } from '../types/auth'

/**
 * Auth module store for handling authentication-specific processes
 * This store delegates global state management to the root auth store
 */
export const useAuthStore = defineStore('auth-module', () => {
  // Local state for authentication processes
  const loading = ref(false)
  const error = ref<string | null>(null)
  const isLoggingOut = ref(false)

  // Get global auth store
  const globalAuthStore = useGlobalAuthStore()

  // Actions
  const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
    try {
      loading.value = true
      error.value = null
      
      const response = await AuthAPI.login(credentials)
      
      // Handle successful login using global auth store
      if (response?.data?.token) {
        // Update global auth state
        globalAuthStore.setAuthState(response.data.user, response.data.token)
        return response.data
      }
      
      throw new Error('Invalid response from server')
    } catch (err: any) {
      error.value = err.message || 'Login failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const register = async (userData: UserRegistrationData): Promise<AuthResponse> => {
    try {
      loading.value = true
      error.value = null
      
      const response = await AuthAPI.register(userData)
      
      // Handle successful registration using global auth store
      if (response?.data?.token) {
        // Update global auth state
        globalAuthStore.setAuthState(response.data.user, response.data.token)
        return response.data
      }
      
      throw new Error('Invalid response from server')
    } catch (err: any) {
      error.value = err.message || 'Registration failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = async (): Promise<void> => {
    if (isLoggingOut.value) return

    try {
      isLoggingOut.value = true
      
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

  return {
    // State
    loading,
    error,
    isLoggingOut,
    
    // Pass through global state for compatibility
    get user() { return globalAuthStore.user },
    get token() { return globalAuthStore.token },
    get isAuthenticated() { return globalAuthStore.isAuthenticated },
    get initialized() { return globalAuthStore.initialized },
    
    // Actions
    login,
    register,
    logout,
    
    // Pass through global actions for compatibility
    initAuth: globalAuthStore.initAuth
  }
})
