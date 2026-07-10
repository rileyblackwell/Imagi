import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// The store instantiates `new PaymentService()` at module load, so the mock
// class must hand back a shared object whose methods we can drive per-test.
const service = vi.hoisted(() => ({
  getBalance: vi.fn(),
  getTransactions: vi.fn(),
  getPaymentMethods: vi.fn(),
  setupCustomer: vi.fn(),
  attachPaymentMethod: vi.fn(),
  createPaymentIntent: vi.fn(),
  processPayment: vi.fn(),
  confirmPayment: vi.fn(),
  verifyPayment: vi.fn(),
  getPlans: vi.fn(),
  getPackages: vi.fn(),
  createCheckoutSession: vi.fn(),
  getSessionStatus: vi.fn(),
  checkCredits: vi.fn(),
  deductCredits: vi.fn(),
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

  describe('fetchBalance', () => {
    it('stores the balance and keeps userCredits in sync', async () => {
      service.getBalance.mockResolvedValue({ balance: 75 })
      const store = usePaymentStore()
      const result = await store.fetchBalance()

      expect(result).toBe(75)
      expect(store.balance).toBe(75)
      expect(store.userCredits).toBe(75)
      expect(store.lastUpdated).not.toBeNull()
      expect(store.isLoadingBalance).toBe(false)
    })

    it('records an error for a malformed response', async () => {
      service.getBalance.mockResolvedValue({ nope: true })
      const store = usePaymentStore()
      const result = await store.fetchBalance()

      expect(result).toBeNull()
      expect(store.error).toBe('Invalid balance response format')
    })

    it('captures thrown errors', async () => {
      service.getBalance.mockRejectedValue(new Error('network down'))
      const store = usePaymentStore()
      const result = await store.fetchBalance()

      expect(result).toBeNull()
      expect(store.error).toBe('network down')
      expect(store.isLoadingBalance).toBe(false)
    })
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

  describe('processPayment', () => {
    it('updates the balance from the new_balance field on success', async () => {
      service.processPayment.mockResolvedValue({ success: true, new_balance: 120 })
      const store = usePaymentStore()
      const result = await store.processPayment({ amount: 20, paymentMethodId: 'pm_1' })

      expect(result.success).toBe(true)
      expect(store.balance).toBe(120)
      expect(store.userCredits).toBe(120)
      expect(store.isProcessingPayment).toBe(false)
    })

    it('propagates errors and resets the processing flag', async () => {
      service.processPayment.mockRejectedValue(new Error('card declined'))
      const store = usePaymentStore()
      await expect(
        store.processPayment({ amount: 20, paymentMethodId: 'pm_1' }),
      ).rejects.toThrow('card declined')
      expect(store.error).toBe('card declined')
      expect(store.isProcessingPayment).toBe(false)
    })
  })

  describe('deductCredits', () => {
    it('updates the balance when the service returns newBalance', async () => {
      service.deductCredits.mockResolvedValue({ success: true, newBalance: 8 })
      const store = usePaymentStore()
      const result = await store.deductCredits(2, 'model run')

      expect(result.newBalance).toBe(8)
      expect(store.balance).toBe(8)
    })
  })

  describe('getSessionStatus', () => {
    it('refreshes the balance when a session completes', async () => {
      service.getSessionStatus.mockResolvedValue({ status: 'complete' })
      service.getBalance.mockResolvedValue({ balance: 200 })
      const store = usePaymentStore()
      await store.getSessionStatus('cs_123')
      expect(service.getBalance).toHaveBeenCalled()
      expect(store.balance).toBe(200)
    })
  })

  describe('resetState', () => {
    it('clears all state back to defaults', async () => {
      service.getBalance.mockResolvedValue({ balance: 50 })
      const store = usePaymentStore()
      await store.fetchBalance()
      expect(store.balance).toBe(50)

      store.resetState()
      expect(store.balance).toBeNull()
      expect(store.userCredits).toBeNull()
      expect(store.transactions).toEqual([])
      expect(store.error).toBeNull()
    })
  })
})
