import { defineStore } from 'pinia'
import axios from 'axios'
import type { 
  PaymentHistoryItem, 
  PaymentStoreState, 
  PaymentProcessRequest, 
  PaymentProcessResponse,
  CreditPackage,
  Transaction
} from '../types'

export const usePaymentsStore = defineStore('payments', {
  state: (): PaymentStoreState => ({
    balance: 0,
    userCredits: 0,
    lastUpdated: null,
    isLoading: false,
    error: null,
    paymentHistory: [],
    isHistoryLoading: false,
    transactions: [],
    packages: []
  }),
  
  getters: {
    formattedBalance: (state): string => `$${state.balance.toFixed(2)}`,
    hasError: (state): boolean => !!state.error,
    currentBalance: (state) => state.balance,
    allTransactions: (state) => state.transactions,
    availablePackages: (state) => state.packages
  },
  
  actions: {
    async fetchBalance(): Promise<void> {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.get<{ balance: number }>('/api/v1/payments/balance/')
        this.balance = response.data.balance
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to fetch balance'
        console.error('Failed to fetch balance:', error)
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchUserCredits(): Promise<void> {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.get<{ credits: number }>('/api/v1/user/credits/')
        this.userCredits = response.data.credits
        this.lastUpdated = new Date()
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to fetch user credits'
        console.error('Failed to fetch user credits:', error)
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchPaymentHistory(): Promise<void> {
      this.isHistoryLoading = true
      
      try {
        const response = await axios.get<{ payments: PaymentHistoryItem[] }>('/api/v1/payments/history/')
        this.paymentHistory = response.data.payments
      } catch (error) {
        console.error('Failed to fetch payment history:', error)
      } finally {
        this.isHistoryLoading = false
      }
    },
    
    async processPayment({ amount, paymentMethodId }: PaymentProcessRequest): Promise<PaymentProcessResponse> {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.post<PaymentProcessResponse>('/api/v1/payments/process/', {
          amount,
          payment_method_id: paymentMethodId
        })
        
        // Update balance after successful payment
        this.balance = response.data.new_balance
        
        // Update user credits
        if (response.data.credits_added) {
          this.userCredits += response.data.credits_added
          this.lastUpdated = new Date()
        }
        
        // Return payment data for further processing
        return response.data
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Payment processing failed'
        console.error('Payment processing failed:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },
    
    async fetchPackages(): Promise<void> {
      this.isLoading = true
      this.error = null
      
      try {
        const response = await axios.get<{ packages: CreditPackage[] }>('/api/v1/payments/packages/')
        // Ensure all packages have a description field to match the type
        this.packages = response.data.packages.map(pkg => ({
          ...pkg,
          description: pkg.description || 'Credit package' // Provide default description if missing
        }))
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to fetch packages'
        console.error('Failed to fetch credit packages:', error)
      } finally {
        this.isLoading = false
      }
    },
    
    clearError(): void {
      this.error = null
    }
  }
})

export default usePaymentsStore 