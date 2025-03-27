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

// Increase cache timeout value to reduce frequent balance API calls
// Only fetch new balance data when explicitly needed
const BALANCE_CACHE_TIMEOUT = 60000 // Increase to 60 seconds (1 minute)

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
  const isAutoRefreshEnabled = ref<boolean>(false) // Disable auto-refresh by default
  // Track last fetch to implement cache
  const lastFetchTime = ref<number>(0)
  const isFetching = ref<boolean>(false)
  // Track pending fetch promises to prevent duplicate requests
  const fetchPromise = ref<Promise<void> | null>(null)
  // Flag for transaction in progress - only fetch during transactions
  const transactionInProgress = ref<boolean>(false)
  
  // Get auth store for user info
  const authStore = useAuthStore()

  // Getters
  const currentBalance = computed(() => balance.value)
  const formattedBalance = computed(() => `${balance.value} credits`)
  
  // Actions
  /**
   * Fetch user's current balance from the API
   * Only fetch when force=true, during transactions, or if cache is stale
   */
  const fetchBalance = async (showLoading: boolean = true, force: boolean = false): Promise<void> => {
    // Check if we have a recent balance and can use the cache
    const now = Date.now()
    const useCachedValue = (
      !force && 
      !transactionInProgress.value &&
      lastFetchTime.value > 0 && 
      now - lastFetchTime.value < BALANCE_CACHE_TIMEOUT && 
      lastUpdated.value !== null
    )
    
    // Return immediately if we should use cached value
    if (useCachedValue) {
      return
    }
    
    // If we're already fetching, return the existing promise
    if (isFetching.value && fetchPromise.value) {
      return fetchPromise.value
    }
    
    // Set loading state if requested
    if (showLoading) {
      loading.value = true
    }
    error.value = null
    isFetching.value = true
    
    // Create a new fetch promise
    const promise = (async () => {
      try {
        const response = await axios.get<{ balance: number }>('/api/v1/payments/balance/')
        balance.value = response.data.balance
        lastUpdated.value = new Date()
        lastFetchTime.value = now
        
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
        isFetching.value = false
        fetchPromise.value = null
        if (showLoading) {
          loading.value = false
        }
        // Reset transaction flag after fetch completes
        transactionInProgress.value = false
      }
    })()
    
    // Store the promise so we can reuse it
    fetchPromise.value = promise
    return promise
  }
  
  /**
   * Start auto-refresh timer for balance (disabled by default)
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
          fetchBalance(false, false) // Don't show loading state for background refreshes
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
   * Indicate that a transaction is in progress
   * Causes the next balance fetch to bypass cache
   */
  const beginTransaction = (): void => {
    transactionInProgress.value = true
  }
  
  /**
   * Update balance locally (used when payments or credits are processed)
   */
  const updateBalance = (newBalance: number): void => {
    balance.value = newBalance
    lastUpdated.value = new Date()
    lastFetchTime.value = Date.now()
    
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
      await fetchBalance(true, true) // Force initial fetch
      // Don't auto-refresh by default
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
    initBalance,
    beginTransaction
  }
}) 