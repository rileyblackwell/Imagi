import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

const apiMock = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('@/shared/services/api', () => ({
  default: apiMock,
  getCsrfToken: vi.fn(),
}))

import { useUsageStore } from '@/shared/stores/usage'

describe('usage store exceededWindow', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    apiMock.get.mockReset()
  })

  it('is null while nothing is known (absent means unknown, not exhausted)', () => {
    const store = useUsageStore()
    expect(store.exceededWindow).toBeNull()

    store.fiveHour = { used: null, limit: 2_000_000, resetsAt: null }
    store.weekly = { used: 1_000, limit: null, resetsAt: null }
    expect(store.exceededWindow).toBeNull()
  })

  it('is null while under both limits', () => {
    const store = useUsageStore()
    store.fiveHour = { used: 100, limit: 2_000_000, resetsAt: null }
    store.weekly = { used: 100, limit: 20_000_000, resetsAt: null }
    expect(store.exceededWindow).toBeNull()
  })

  it('reports the five-hour window first, matching the backend check order', () => {
    const store = useUsageStore()
    store.fiveHour = { used: 2_000_000, limit: 2_000_000, resetsAt: null }
    store.weekly = { used: 20_000_000, limit: 20_000_000, resetsAt: null }
    expect(store.exceededWindow).toBe('5h')
  })

  it('reports the weekly window when only it is exhausted', () => {
    const store = useUsageStore()
    store.fiveHour = { used: 100, limit: 2_000_000, resetsAt: null }
    store.weekly = { used: 20_000_001, limit: 20_000_000, resetsAt: null }
    expect(store.exceededWindow).toBe('week')
  })
})
