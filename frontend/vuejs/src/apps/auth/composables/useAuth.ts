import { useAuthStore } from '../stores/index'
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
