import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import PaymentService from '../services/payment_service'
import type { 
  PaymentMethod, 
  TransactionHistoryItem, 
  Plan, 
  CreditPackage,
  Transaction
} from '../types'

const paymentService = new PaymentService()

export const usePaymentStore = defineStore('payments', () => {
  // State
  const balance: Ref<number | null> = ref(null)
  const isLoadingBalance: Ref<boolean> = ref(false)
  const transactions: Ref<Transaction[]> = ref([])
  const totalTransactions: Ref<number> = ref(0)
  const isLoadingTransactions: Ref<boolean> = ref(false)
  const paymentMethods: Ref<PaymentMethod[]> = ref([])
  const isLoadingPaymentMethods: Ref<boolean> = ref(false)
  const plans: Ref<Plan[]> = ref([])
  const isLoadingPlans: Ref<boolean> = ref(false)
  const packages: Ref<CreditPackage[]> = ref([])
  const isLoadingPackages: Ref<boolean> = ref(false)
  const error: Ref<string | null> = ref(null)
  const isProcessingPayment: Ref<boolean> = ref(false)

  // Computed
  const hasPaymentMethods = computed(() => paymentMethods.value.length > 0)
  const defaultPaymentMethod = computed(() => 
    paymentMethods.value.find(pm => pm.is_default) || paymentMethods.value[0] || null
  )

  // Actions
  async function fetchBalance() {
    isLoadingBalance.value = true
    error.value = null
    
    try {
      const response = await paymentService.getBalance()
      balance.value = response.balance
      return response.balance
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch balance'
      console.error('Error fetching balance:', err)
      return null
    } finally {
      isLoadingBalance.value = false
    }
  }

  async function fetchTransactions(filters = {}) {
    isLoadingTransactions.value = true
    error.value = null
    
    try {
      const response = await paymentService.getTransactions(filters)
      transactions.value = response.transactions || []
      totalTransactions.value = response.total_count || 0
      return response
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch transactions'
      console.error('Error fetching transactions:', err)
      return { transactions: [], total_count: 0 }
    } finally {
      isLoadingTransactions.value = false
    }
  }

  async function fetchTransactionHistory() {
    isLoadingTransactions.value = true
    error.value = null
    
    try {
      const history = await paymentService.getTransactionHistory()
      return history
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch transaction history'
      console.error('Error fetching transaction history:', err)
      return []
    } finally {
      isLoadingTransactions.value = false
    }
  }

  async function fetchPaymentMethods() {
    isLoadingPaymentMethods.value = true
    error.value = null
    
    try {
      const methods = await paymentService.getPaymentMethods()
      paymentMethods.value = methods
      return methods
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch payment methods'
      console.error('Error fetching payment methods:', err)
      return []
    } finally {
      isLoadingPaymentMethods.value = false
    }
  }

  async function setupCustomer() {
    error.value = null
    
    try {
      return await paymentService.setupCustomer()
    } catch (err: any) {
      error.value = err.message || 'Failed to setup customer'
      console.error('Error setting up customer:', err)
      throw err
    }
  }

  async function attachPaymentMethod(paymentMethodId: string) {
    error.value = null
    
    try {
      const result = await paymentService.attachPaymentMethod(paymentMethodId)
      await fetchPaymentMethods() // Refresh the list
      return result
    } catch (err: any) {
      error.value = err.message || 'Failed to attach payment method'
      console.error('Error attaching payment method:', err)
      throw err
    }
  }

  async function createPaymentIntent(amount: number) {
    error.value = null
    
    try {
      return await paymentService.createPaymentIntent({ amount })
    } catch (err: any) {
      error.value = err.message || 'Failed to create payment intent'
      console.error('Error creating payment intent:', err)
      throw err
    }
  }

  async function processPayment(amount: number, paymentMethodId: string) {
    isProcessingPayment.value = true
    error.value = null
    
    try {
      const result = await paymentService.processPayment(amount, paymentMethodId)
      
      // If payment was successful, update the balance
      if (result.success || result.new_balance) {
        balance.value = result.new_balance
      }
      
      return result
    } catch (err: any) {
      error.value = err.message || 'Failed to process payment'
      console.error('Error processing payment:', err)
      throw err
    } finally {
      isProcessingPayment.value = false
    }
  }

  async function confirmPayment(paymentIntentId: string) {
    isProcessingPayment.value = true
    error.value = null
    
    try {
      const result = await paymentService.confirmPayment(paymentIntentId)
      
      // If payment was confirmed, update the balance
      if (result.new_balance) {
        balance.value = result.new_balance
      }
      
      return result
    } catch (err: any) {
      error.value = err.message || 'Failed to confirm payment'
      console.error('Error confirming payment:', err)
      throw err
    } finally {
      isProcessingPayment.value = false
    }
  }

  async function verifyPayment(paymentIntentId: string) {
    error.value = null
    
    try {
      const result = await paymentService.verifyPayment(paymentIntentId)
      
      // If payment verification returned a new balance, update it
      if (result.new_balance) {
        balance.value = result.new_balance
      }
      
      return result
    } catch (err: any) {
      error.value = err.message || 'Failed to verify payment'
      console.error('Error verifying payment:', err)
      throw err
    }
  }

  async function fetchPlans() {
    isLoadingPlans.value = true
    error.value = null
    
    try {
      const fetchedPlans = await paymentService.getPlans()
      plans.value = fetchedPlans
      return fetchedPlans
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch plans'
      console.error('Error fetching plans:', err)
      return []
    } finally {
      isLoadingPlans.value = false
    }
  }

  async function fetchPackages() {
    isLoadingPackages.value = true
    error.value = null
    
    try {
      const fetchedPackages = await paymentService.getPackages()
      packages.value = fetchedPackages
      return fetchedPackages
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch packages'
      console.error('Error fetching packages:', err)
      return []
    } finally {
      isLoadingPackages.value = false
    }
  }

  async function createCheckoutSession(amount: number, planId?: string) {
    error.value = null
    
    try {
      return await paymentService.createCheckoutSession({
        amount: amount,
        plan_id: planId
      })
    } catch (err: any) {
      error.value = err.message || 'Failed to create checkout session'
      console.error('Error creating checkout session:', err)
      throw err
    }
  }

  async function getSessionStatus(sessionId: string) {
    error.value = null
    
    try {
      const result = await paymentService.getSessionStatus(sessionId)
      
      // If payment was successful, update the balance
      if (result.status === 'complete') {
        await fetchBalance() // Refresh balance
      }
      
      return result
    } catch (err: any) {
      error.value = err.message || 'Failed to get session status'
      console.error('Error getting session status:', err)
      throw err
    }
  }

  async function checkCredits(requiredCredits: number) {
    error.value = null
    
    try {
      return await paymentService.checkCredits(requiredCredits)
    } catch (err: any) {
      error.value = err.message || 'Failed to check credits'
      console.error('Error checking credits:', err)
      throw err
    }
  }

  async function deductCredits(credits: number, description?: string) {
    error.value = null
    
    try {
      const result = await paymentService.deductCredits(credits, description)
      
      // Update balance if deduction was successful
      if (result.new_balance !== undefined) {
        balance.value = result.new_balance
      }
      
      return result
    } catch (err: any) {
      error.value = err.message || 'Failed to deduct credits'
      console.error('Error deducting credits:', err)
      throw err
    }
  }

  // Reset store state
  function resetState() {
    balance.value = null
    transactions.value = []
    totalTransactions.value = 0
    paymentMethods.value = []
    plans.value = []
    packages.value = []
    error.value = null
  }

  return {
    // State
    balance,
    isLoadingBalance,
    transactions,
    totalTransactions,
    isLoadingTransactions,
    paymentMethods,
    isLoadingPaymentMethods,
    plans,
    isLoadingPlans,
    packages,
    isLoadingPackages,
    error,
    isProcessingPayment,
    
    // Computed
    hasPaymentMethods,
    defaultPaymentMethod,
    
    // Actions
    fetchBalance,
    fetchTransactions,
    fetchTransactionHistory,
    fetchPaymentMethods,
    setupCustomer,
    attachPaymentMethod,
    createPaymentIntent,
    processPayment,
    confirmPayment,
    verifyPayment,
    fetchPlans,
    fetchPackages,
    createCheckoutSession,
    getSessionStatus,
    checkCredits,
    deductCredits,
    resetState
  }
}) 