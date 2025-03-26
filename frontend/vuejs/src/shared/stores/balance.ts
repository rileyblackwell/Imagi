import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from './auth'

// Helper function for safely parsing JSON
const safeJSONParse = <T>(jsonString: string | null, fallback: T): T => {
  if (!jsonString) return fallback
  try {
    return JSON.parse(jsonString) as T
  } catch (e) {
    return fallback
  }
}

/**
 * Global balance store for managing user account balance across the application
 */
export const useBalanceStore = defineStore('global-balance', () => {
  // State
  const balance = ref<number>(0)
  const lastUpdated = ref<Date | null>(null)
  const loading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const refreshTimer = ref<ReturnType<typeof setInterval> | null>(null)
  const isAutoRefreshEnabled = ref<boolean>(true)
  
  // Get auth store for user info
  const authStore = useAuthStore()

  // Getters
  const currentBalance = computed(() => balance.value)
  const formattedBalance = computed(() => `${balance.value} credits`)
  
  // Actions
  /**
   * Fetch user's current balance from the API
   */
  const fetchBalance = async (showLoading: boolean = true): Promise<void> => {
    if (showLoading) {
      loading.value = true
    }
    error.value = null
    
    try {
      const response = await axios.get<{ balance: number }>('/api/v1/payments/balance/')
      balance.value = response.data.balance
      lastUpdated.value = new Date()
      
      // Also update the user object in auth store if it exists
      if (authStore.user && typeof authStore.user === 'object') {
        authStore.user = {
          ...authStore.user,
          balance: response.data.balance
        }
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch balance'
      console.error('Failed to fetch balance:', err)
    } finally {
      if (showLoading) {
        loading.value = false
      }
    }
  }
  
  /**
   * Start auto-refresh timer for balance
   */
  const startAutoRefresh = (interval: number = 60000): void => {
    // Clear any existing timer
    if (refreshTimer.value) {
      clearInterval(refreshTimer.value)
    }
    
    // Only start if auto-refresh is enabled
    if (isAutoRefreshEnabled.value) {
      refreshTimer.value = setInterval(() => {
        if (authStore.isAuthenticated) {
          fetchBalance(false) // Don't show loading state for background refreshes
        }
      }, interval)
    }
  }
  
  /**
   * Stop auto-refresh timer
   */
  const stopAutoRefresh = (): void => {
    if (refreshTimer.value) {
      clearInterval(refreshTimer.value)
      refreshTimer.value = null
    }
  }
  
  /**
   * Toggle auto-refresh setting
   */
  const toggleAutoRefresh = (enabled?: boolean): void => {
    isAutoRefreshEnabled.value = enabled !== undefined ? enabled : !isAutoRefreshEnabled.value
    
    if (isAutoRefreshEnabled.value) {
      startAutoRefresh()
    } else {
      stopAutoRefresh()
    }
  }
  
  /**
   * Update balance locally (used when payments or credits are processed)
   */
  const updateBalance = (newBalance: number): void => {
    balance.value = newBalance
    lastUpdated.value = new Date()
    
    // Also update the user object in auth store if it exists
    if (authStore.user && typeof authStore.user === 'object') {
      authStore.user = {
        ...authStore.user,
        balance: newBalance
      }
    }
  }
  
  /**
   * Reset balance store
   */
  const resetBalance = (): void => {
    balance.value = 0
    lastUpdated.value = null
    error.value = null
    stopAutoRefresh()
  }
  
  /**
   * Initialize balance on app startup
   */
  const initBalance = async (): Promise<void> => {
    // Only fetch if user is authenticated
    if (authStore.isAuthenticated) {
      await fetchBalance()
      startAutoRefresh()
    } else {
      resetBalance()
    }
  }
  
  return {
    // State
    balance,
    lastUpdated,
    loading,
    error,
    isAutoRefreshEnabled,
    
    // Getters
    currentBalance,
    formattedBalance,
    
    // Actions
    fetchBalance,
    startAutoRefresh,
    stopAutoRefresh,
    toggleAutoRefresh,
    updateBalance,
    resetBalance,
    initBalance
  }
}) 