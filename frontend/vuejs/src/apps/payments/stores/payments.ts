import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Ref } from 'vue'
import PaymentService from '../services/payment_service'

/**
 * Billing store. The pricing page and the billing portal call PaymentService
 * directly; this store only backs the post-checkout success page.
 *
 * There is no balance here. Access is metered against a plan allowance in
 * dollars — see the usage store (@/shared/stores/usage), which is the
 * workspace's spend surface.
 */

const paymentService = new PaymentService()

export const usePaymentStore = defineStore('payments', () => {
  const error: Ref<string | null> = ref(null)

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

  return {
    error,
    getSessionStatus,
  }
})
