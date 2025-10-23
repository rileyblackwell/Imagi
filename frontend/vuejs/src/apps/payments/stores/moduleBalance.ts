import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/shared/services/api'
import { useBalanceStore as useGlobalBalanceStore } from '@/shared/stores/balance'
import type { 
  PaymentHistoryItem, 
  PaymentProcessResponse,
  CreditPackage,
  Transaction
} from '../types'

/**
 * Payments module balance store for handling payment-specific operations
 * This store delegates global balance state management to the shared balance store
 * while providing payment-specific functionality
 */
export const useModuleBalanceStore = defineStore('payments-module-balance', () => {
  // Local state for payment processes
  const loading = ref(false)
  const error = ref<string | null>(null)
  const paymentHistory = ref<PaymentHistoryItem[]>([])
  const isHistoryLoading = ref(false)
  const transactions = ref<Transaction[]>([])
  const packages = ref<CreditPackage[]>([])
  const isPackagesLoading = ref(false)
  
  // Get global balance store
  const globalBalanceStore = useGlobalBalanceStore()
  
  // Computed properties
  const balance = computed(() => globalBalanceStore.balance)
  const lastUpdated = computed(() => globalBalanceStore.lastUpdated)
  const formattedBalance = computed(() => globalBalanceStore.formattedBalance)
  
  // Actions
  /**
   * Fetch available credit packages
   */
  const fetchPackages = async (): Promise<void> => {
    try {
      isPackagesLoading.value = true
      error.value = null
      
      const response = await api.get<CreditPackage[]>('/v1/payments/packages/')
      packages.value = response.data
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch packages'
      console.error('Failed to fetch packages:', err)
    } finally {
      isPackagesLoading.value = false
    }
  }
  
  /**
   * Fetch transaction history
   */
  const fetchTransactions = async (): Promise<void> => {
    try {
      isHistoryLoading.value = true
      error.value = null
      
      const response = await api.get<Transaction[]>('/v1/payments/transactions/')
      transactions.value = response.data
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch transactions'
      console.error('Failed to fetch transactions:', err)
    } finally {
      isHistoryLoading.value = false
    }
  }
  
  /**
   * Process a payment
   */
  const processPayment = async (amount: number, paymentMethodId: string): Promise<PaymentProcessResponse> => {
    try {
      loading.value = true
      error.value = null
      
      const response = await api.post<PaymentProcessResponse>('/v1/payments/process/', {
        amount,
        payment_method_id: paymentMethodId
      })
      
      // Update global balance if payment was successful
      if (response.data.success && response.data.new_balance !== undefined) {
        globalBalanceStore.updateBalance(response.data.new_balance)
      }
      
      return response.data
    } catch (err: any) {
      error.value = err.message || 'Payment failed'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Wrapper for global balance fetch
   */
  const fetchBalance = async (): Promise<number | undefined> => {
    return globalBalanceStore.fetchBalance()
  }
  
  return {
    // State
    loading,
    error,
    paymentHistory,
    isHistoryLoading,
    transactions,
    packages,
    isPackagesLoading,
    
    // Computed properties that expose global state
    balance,
    lastUpdated,
    formattedBalance,
    
    // Actions
    fetchPackages,
    fetchTransactions,
    processPayment,
    fetchBalance
  }
}) 