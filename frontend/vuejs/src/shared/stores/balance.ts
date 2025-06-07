import { defineStore } from 'pinia'
import api, { buildApiUrl } from '@/shared/services/api'


interface BalanceState {
  balance: number;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

/**
 * Global balance store for managing user account balance across the application
 */
export const useBalanceStore = defineStore('global-balance', {
  state: (): BalanceState => ({
    balance: 0,
    loading: false,
    error: null,
    lastUpdated: null
  }),

  getters: {
    formattedBalance: (state) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(state.balance)
    },
    isStale: (state) => {
      if (!state.lastUpdated) return true
      const staleThreshold = 5 * 60 * 1000 // 5 minutes
      return Date.now() - new Date(state.lastUpdated).getTime() > staleThreshold
    }
  },

  actions: {
    async fetchBalance(showLoading: boolean = true, forceRefresh: boolean = false) {
      this.loading = showLoading
      this.error = null
      
      try {
        // Ignore forceRefresh parameter but still use it as a valid parameter
        // to maintain compatibility with existing calls
        const response = await api.get<{ balance: number }>(buildApiUrl('/api/v1/payments/balance/'))
        this.balance = response.data.balance
        this.lastUpdated = new Date().toISOString()
        return response.data.balance
      } catch (error: any) {
        console.error('Error fetching balance:', error)
        this.error = error.message || 'Failed to fetch balance'
        throw error
      } finally {
        this.loading = showLoading
      }
    },

    async refreshIfStale() {
      if (this.isStale) {
        await this.fetchBalance()
      }
    },

    updateBalance(newBalance: number) {
      this.balance = newBalance
      this.lastUpdated = new Date().toISOString()
    },

    beginTransaction() {
      this.loading = true
      this.error = null
    },

    completeTransaction(newBalance?: number) {
      this.loading = false
      if (typeof newBalance === 'number') {
        this.updateBalance(newBalance)
      }
    },

    failTransaction(error: string) {
      this.loading = false
      this.error = error
    },

    clearError() {
      this.error = null
    },

    /**
     * Initialize balance (fetch initial balance from API)
     */
    initBalance() {
      // Initialize with stored balance if available
      this.fetchBalance()
    },
    
    /**
     * Reset balance state to default values
     */
    resetBalance() {
      this.balance = 0
      this.loading = false
      this.error = null
      this.lastUpdated = null
    },

    /**
     * Alias for resetBalance for backward compatibility
     */
    reset() {
      this.resetBalance()
    }
  }
})