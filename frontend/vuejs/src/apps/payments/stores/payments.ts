import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Ref } from 'vue'
import PaymentService from '../services/payment_service'
import type { PaymentMethod, Transaction } from '../types'

/**
 * Billing store: subscription checkout, the Stripe billing portal, saved
 * payment methods, and the read-only purchase history.
 *
 * There is no balance here. Access is metered against a plan allowance in
 * dollars — see the usage store (@/shared/stores/usage), which is the
 * workspace's spend surface.
 */

const paymentService = new PaymentService()

export const usePaymentStore = defineStore('payments', () => {
  // State
  const lastUpdated: Ref<string | null> = ref(null)
  const isLoading: Ref<boolean> = ref(false)
  const transactions: Ref<Transaction[]> = ref([])
  const totalTransactions: Ref<number> = ref(0)
  const isLoadingTransactions: Ref<boolean> = ref(false)
  const paymentMethods: Ref<PaymentMethod[]> = ref([])
  const isLoadingPaymentMethods: Ref<boolean> = ref(false)
  const error: Ref<string | null> = ref(null)

  // Computed
  const hasPaymentMethods = computed(() => paymentMethods.value.length > 0)
  const defaultPaymentMethod = computed(() =>
    paymentMethods.value.find(pm => pm.is_default) || paymentMethods.value[0] || null
  )

  // Actions
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

  /** Start Stripe Checkout for a subscription plan, named by its lookup_key. */
  async function createCheckoutSession(lookupKey: string) {
    error.value = null

    try {
      return await paymentService.createCheckoutSession({ lookup_key: lookupKey })
    } catch (err: any) {
      error.value = err.message || 'Failed to create checkout session'
      console.error('Error creating checkout session:', err)
      throw err
    }
  }

  /** Open the Stripe Billing Portal to change or cancel a subscription. */
  async function createPortalSession(returnUrl?: string) {
    error.value = null

    try {
      return await paymentService.createPortalSession(returnUrl)
    } catch (err: any) {
      error.value = err.message || 'Failed to open the billing portal'
      console.error('Error creating portal session:', err)
      throw err
    }
  }

  async function getSessionStatus(sessionId: string) {
    error.value = null

    try {
      // Informational only — the plan itself is granted by Stripe's
      // subscription webhook, not by reading the session back.
      return await paymentService.getSessionStatus(sessionId)
    } catch (err: any) {
      error.value = err.message || 'Failed to get session status'
      console.error('Error getting session status:', err)
      throw err
    }
  }

  // Reset store state
  function resetState() {
    transactions.value = []
    totalTransactions.value = 0
    paymentMethods.value = []
    error.value = null
    lastUpdated.value = null
    isLoading.value = false
  }

  return {
    // State
    lastUpdated,
    isLoading,
    transactions,
    totalTransactions,
    isLoadingTransactions,
    paymentMethods,
    isLoadingPaymentMethods,
    error,

    // Computed
    hasPaymentMethods,
    defaultPaymentMethod,

    // Actions
    fetchTransactions,
    fetchPaymentMethods,
    setupCustomer,
    attachPaymentMethod,
    createCheckoutSession,
    createPortalSession,
    getSessionStatus,
    resetState
  }
})
