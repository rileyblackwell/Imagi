import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// The store instantiates `new PaymentService()` at module load, so the mock
// class must hand back a shared object whose methods we can drive per-test.
const service = vi.hoisted(() => ({
  getTransactions: vi.fn(),
  getPaymentMethods: vi.fn(),
  setupCustomer: vi.fn(),
  attachPaymentMethod: vi.fn(),
  createCheckoutSession: vi.fn(),
  createPortalSession: vi.fn(),
  getSessionStatus: vi.fn(),
}))
vi.mock('../../services/payment_service', () => ({
  // Returning an object from the constructor makes `new PaymentService()`
  // resolve to our shared mock.
  default: class {
    constructor() {
      return service
    }
  },
}))

import { usePaymentStore } from '@/apps/payments/stores/payments'

describe('payments store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    Object.values(service).forEach((fn) => fn.mockReset())
  })

  describe('fetchTransactions', () => {
    it('stores transactions and total count', async () => {
      service.getTransactions.mockResolvedValue({
        transactions: [{ id: 1 }, { id: 2 }],
        total_count: 2,
      })
      const store = usePaymentStore()
      await store.fetchTransactions()

      expect(store.transactions).toHaveLength(2)
      expect(store.totalTransactions).toBe(2)
    })
  })

  describe('fetchPaymentMethods + computed', () => {
    it('populates methods and derives hasPaymentMethods / defaultPaymentMethod', async () => {
      const methods = [
        { id: 'pm_1', is_default: false },
        { id: 'pm_2', is_default: true },
      ]
      service.getPaymentMethods.mockResolvedValue(methods)
      const store = usePaymentStore()

      expect(store.hasPaymentMethods).toBe(false)
      await store.fetchPaymentMethods()

      expect(store.hasPaymentMethods).toBe(true)
      expect(store.defaultPaymentMethod).toEqual({ id: 'pm_2', is_default: true })
    })

    it('falls back to the first method when none is marked default', async () => {
      service.getPaymentMethods.mockResolvedValue([
        { id: 'pm_1', is_default: false },
        { id: 'pm_2', is_default: false },
      ])
      const store = usePaymentStore()
      await store.fetchPaymentMethods()
      expect(store.defaultPaymentMethod).toEqual({ id: 'pm_1', is_default: false })
    })
  })

  describe('createCheckoutSession', () => {
    it('checks out by the plan lookup_key', async () => {
      // Subscriptions are the only thing sold, so the lookup_key — not a
      // dollar amount — is what identifies the purchase.
      service.createCheckoutSession.mockResolvedValue({
        session_id: 'cs_1', checkout_url: 'https://checkout.test/cs_1',
      })
      const store = usePaymentStore()
      const result = await store.createCheckoutSession('pro_monthly')

      expect(service.createCheckoutSession).toHaveBeenCalledWith({
        lookup_key: 'pro_monthly',
      })
      expect(result.checkout_url).toBe('https://checkout.test/cs_1')
    })

    it('records and rethrows errors', async () => {
      service.createCheckoutSession.mockRejectedValue(new Error('card declined'))
      const store = usePaymentStore()
      await expect(store.createCheckoutSession('pro_monthly')).rejects.toThrow('card declined')
      expect(store.error).toBe('card declined')
    })
  })

  describe('createPortalSession', () => {
    it('returns the Stripe billing portal url', async () => {
      service.createPortalSession.mockResolvedValue({ url: 'https://portal.test/s' })
      const store = usePaymentStore()
      const result = await store.createPortalSession()
      expect(result.url).toBe('https://portal.test/s')
    })
  })

  describe('resetState', () => {
    it('clears all state back to defaults', async () => {
      service.getTransactions.mockResolvedValue({
        transactions: [{ id: 1 }], total_count: 1,
      })
      const store = usePaymentStore()
      await store.fetchTransactions()
      expect(store.transactions).toHaveLength(1)

      store.resetState()
      expect(store.transactions).toEqual([])
      expect(store.totalTransactions).toBe(0)
      expect(store.error).toBeNull()
    })
  })
})
