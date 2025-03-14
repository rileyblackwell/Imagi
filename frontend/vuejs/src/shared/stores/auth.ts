import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import axios from 'axios'
import type { User } from '@/apps/auth/types/auth'

// Define token data structure interface
interface TokenData {
  value: string;
  expires: number;
}

// Create a function to safely parse JSON with a fallback
const safeJSONParse = <T>(jsonString: string | null, fallback: T): T => {
  if (!jsonString) return fallback
  try {
    return JSON.parse(jsonString) as T
  } catch {
    return fallback
  }
}

/**
 * Global authentication store for managing user sessions across the application
 */
export const useAuthStore = defineStore('global-auth', () => {
  // State
  const token = ref<string | null>(getStoredToken())
  const user = ref<User | null>(getStoredUser())
  const isAuthenticated = ref(!!token.value)
  const sessionTimeout = ref<number | null>(null)
  const initialized = ref(false)
  const loading = ref(false)
  const lastInitTime = ref<number>(0)
  
  // Watch for changes to authentication state and sync with localStorage
  watch(() => isAuthenticated.value, (newValue) => {
    if (newValue && token.value && user.value) {
      // If becoming authenticated, make sure token is set in axios
      axios.defaults.headers.common['Authorization'] = `Token ${token.value}`
    }
  })

  // Helper function to get the stored token
  function getStoredToken(): string | null {
    try {
      const tokenData = safeJSONParse<TokenData | null>(localStorage.getItem('token'), null)
      if (!tokenData?.value) return null
      if (tokenData.expires && Date.now() > tokenData.expires) {
        localStorage.removeItem('token')
        return null
      }
      return tokenData.value
    } catch {
      return null
    }
  }

  // Helper function to get the stored user
  function getStoredUser(): User | null {
    return safeJSONParse(localStorage.getItem('user'), null)
  }

  // Getters
  const currentUser = computed(() => user.value)
  const userBalance = computed(() => user.value?.balance || 0)

  // Actions
  const setAuthState = (userData: User | null, authToken: string | null) => {
    user.value = userData
    token.value = authToken
    isAuthenticated.value = !!authToken
    
    if (authToken && userData) {
      // Store token in localStorage with expiry
      const tokenData: TokenData = {
        value: authToken,
        expires: Date.now() + (24 * 60 * 60 * 1000) // 24 hours
      }
      localStorage.setItem('token', JSON.stringify(tokenData))
      localStorage.setItem('user', JSON.stringify(userData))
      
      // Set axios default auth header
      axios.defaults.headers.common['Authorization'] = `Token ${authToken}`
      sessionTimeout.value = 30 * 60 * 1000 // 30 minutes
    } else {
      clearStoredAuth()
    }
  }
  
  // Function to restore auth state from localStorage without API calls
  // Used primarily during browser navigation events
  const restoreAuthState = (userData: User, authToken: string) => {
    user.value = userData
    token.value = authToken
    isAuthenticated.value = true
    
    // Set axios default auth header
    axios.defaults.headers.common['Authorization'] = `Token ${authToken}`
    
    console.log('Auth state restored from localStorage')
  }

  // Helper to clear stored authentication data
  const clearStoredAuth = () => {
    // Clear localStorage items
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    
    // Also clear any potential session/auth cookies
    document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
    document.cookie = 'auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
    document.cookie = 'sessionid=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
    
    // Remove auth header
    delete axios.defaults.headers.common['Authorization']
    sessionTimeout.value = null
  }

  const initAuth = async () => {
    // Don't re-initialize too frequently to avoid unnecessary API calls
    const now = Date.now()
    if (initialized.value && (now - lastInitTime.value) < 5000) {
      // If token exists, make sure authentication state is set properly
      if (token.value && !isAuthenticated.value) {
        isAuthenticated.value = true
        axios.defaults.headers.common['Authorization'] = `Token ${token.value}`
      }
      return
    }
    
    lastInitTime.value = now
    
    try {
      loading.value = true
      
      // Check if we have a token in localStorage
      const storedToken = getStoredToken()
      const storedUser = getStoredUser()
      
      if (!storedToken) {
        // No token found, ensure we're in a clean state
        await clearAuth()
        loading.value = false
        initialized.value = true
        return
      }
      
      // We have a token, set it in axios headers
      token.value = storedToken
      user.value = storedUser
      axios.defaults.headers.common['Authorization'] = `Token ${storedToken}`
      
      try {
        // Check auth status with backend
        const response = await axios.get('/api/v1/auth/init/')
        
        if (response.data.isAuthenticated) {
          // Update user data from server
          user.value = response.data.user
          isAuthenticated.value = true
          
          // Update stored user data
          localStorage.setItem('user', JSON.stringify(response.data.user))
        } else {
          // Session invalid on server
          await clearAuth()
        }
      } catch (error) {
        console.error('Failed to validate auth with server:', error)
        // Keep the token for now, but mark as not authenticated
        // This allows components to handle auth errors gracefully
        isAuthenticated.value = false
      }
    } catch (error) {
      console.error('Failed to initialize auth:', error)
      await clearAuth()
    } finally {
      loading.value = false
      initialized.value = true
    }
  }

  // Method to check auth status without side effects
  const checkAuth = async (): Promise<boolean> => {
    if (!token.value) return false
    
    try {
      axios.defaults.headers.common['Authorization'] = `Token ${token.value}`
      const response = await axios.get('/api/v1/auth/init/')
      return !!response.data.isAuthenticated
    } catch {
      return false
    }
  }

  const validateAuth = async () => {
    try {
      loading.value = true
      
      if (!token.value) {
        return false
      }
      
      axios.defaults.headers.common['Authorization'] = `Token ${token.value}`
      const response = await axios.get('/api/v1/auth/init/')
      
      if (response.data.isAuthenticated) {
        // Update user data from server
        user.value = response.data.user
        isAuthenticated.value = true
        
        // Update stored user data
        localStorage.setItem('user', JSON.stringify(response.data.user))
        return true
      } else {
        await clearAuth()
        return false
      }
    } catch (error) {
      console.error('Auth validation error:', error)
      await clearAuth()
      return false
    } finally {
      loading.value = false
    }
  }

  const clearAuth = async () => {
    // Clear state
    user.value = null
    token.value = null
    isAuthenticated.value = false
    
    // Clear stored data and headers
    clearStoredAuth()
    
    // Reset initialization flag to ensure proper re-initialization if needed
    initialized.value = false
  }

  // Add logout method that simply calls clearAuth for better semantics
  const logout = async () => {
    return await clearAuth()
  }

  const refreshToken = async () => {
    try {
      const response = await axios.post('/api/v1/auth/refresh-token/')
      if (response.data.token) {
        setAuthState(response.data.user, response.data.token)
        return true
      }
      return false
    } catch (error) {
      console.error('Token refresh failed:', error)
      return false
    }
  }

  // Return store properties and methods
  return {
    // State
    token,
    user,
    isAuthenticated,
    sessionTimeout,
    initialized,
    loading,
    
    // Getters
    currentUser,
    userBalance,
    
    // Actions
    setAuthState,
    restoreAuthState,
    initAuth,
    checkAuth,
    validateAuth,
    clearAuth,
    logout,
    refreshToken
  }
}) 