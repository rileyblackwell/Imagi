import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/shared/services/api'
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
    async fetchBalance() {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.get<{ balance: number }>('/api/v1/payments/balance/')
        this.balance = response.data.balance
        this.lastUpdated = new Date().toISOString()
      } catch (error: any) {
        console.error('Error fetching balance:', error)
        this.error = error.message || 'Failed to fetch balance'
        throw error
      } finally {
        this.loading = false
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

    reset() {
      this.balance = 0
      this.loading = false
      this.error = null
      this.lastUpdated = null
    }
  }
}) 