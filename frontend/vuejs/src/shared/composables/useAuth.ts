import { ref, computed, type ComputedRef } from 'vue'

interface AuthState {
  isAuthenticated: ComputedRef<boolean>
  setAuthenticated: (status: boolean) => void
}

export function useAuth(): AuthState {
  // Get initial auth state from localStorage or cookie
  const getInitialAuthState = () => {
    const token = localStorage.getItem('auth_token') || 
      document.cookie.split('; ').find(row => row.startsWith('auth_token='))
    return !!token
  }

  const authState = ref(getInitialAuthState())

  const isAuthenticated = computed(() => authState.value)

  const setAuthenticated = (status: boolean) => {
    authState.value = status
    if (!status) {
      // Clear auth token
      localStorage.removeItem('auth_token')
      // Clear auth cookie if it exists
      document.cookie = 'auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
    }
  }

  return {
    isAuthenticated,
    setAuthenticated
  }
} 