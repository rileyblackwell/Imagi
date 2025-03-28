// Re-export the payments store for easier importing
export { default as usePaymentsStore } from './payments'
export * from './payments'

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { useBalanceStore } from '@/shared/stores/balance'
import type { 
  PaymentHistoryItem, 
  PaymentProcessRequest, 
  PaymentProcessResponse,
  CreditPackage,
  Transaction
} from '../types'

/**
 * Payments module store for handling payment-specific processes
 * This store manages local payment state for processing payments 
 * while delegating global balance state management to the root balance store
 */
export const usePaymentsModuleStore = defineStore('payments-module', () => {
  // Local state for payment processes
  const loading = ref(false)
  const error = ref<string | null>(null)
  const paymentHistory = ref<PaymentHistoryItem[]>([])
  const isHistoryLoading = ref(false)
  const transactions = ref<Transaction[]>([])
  const packages = ref<CreditPackage[]>([])
  const isPackagesLoading = ref(false)
  
  // Get global balance store
  const balanceStore = useBalanceStore()
  
  // Computed properties
  const balance = computed(() => balanceStore.balance)
  const lastUpdated = computed(() => balanceStore.lastUpdated)
  
  // Actions
  /**
   * Fetch available credit packages
   */
  const fetchPackages = async (): Promise<void> => {
    try {
      isPackagesLoading.value = true
      error.value = null
      
      const response = await axios.get<CreditPackage[]>('/api/v1/payments/packages/')
      packages.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch packages'
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
      
      const response = await axios.get<Transaction[]>('/api/v1/payments/transactions/')
      transactions.value = response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch transactions'
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
      
      const response = await axios.post<PaymentProcessResponse>('/api/v1/payments/process/', {
        amount,
        payment_method_id: paymentMethodId
      })
      
      // Update global balance if payment was successful
      if (response.data.success && response.data.new_balance !== undefined) {
        balanceStore.updateBalance(response.data.new_balance)
      }
      
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Payment failed'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  /**
   * Wrapper for global balance fetch
   */
  const fetchBalance = async (): Promise<void> => {
    return balanceStore.fetchBalance()
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
    
    // Actions
    fetchPackages,
    fetchTransactions,
    processPayment,
    fetchBalance
  }
}) 