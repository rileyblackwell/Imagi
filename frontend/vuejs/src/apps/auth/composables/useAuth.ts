import { useAuthStore } from '../store'
import type { User } from '../types/auth'

export function useAuth() {
  const store = useAuthStore()

  return {
    // State
    user: store.user,
    isAuthenticated: store.isAuthenticated,
    loading: store.loading,
    error: store.error,

    // Actions
    login: store.login,
    logout: store.logout,
    register: store.register,
    updateUser: store.updateUser,
    initAuth: store.initAuth
  }
}

export type { User }
