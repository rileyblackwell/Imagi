import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

const apiMock = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('@/shared/services/api', () => ({
  default: apiMock,
}))

import { useUsageStore, formatUsd } from '@/shared/stores/usage'

// Free-plan allowance: $10/week. Weekly is the only window.
const WEEKLY = 10

describe('usage store exceededWindow', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    apiMock.get.mockReset()
  })

  it('is null while nothing is known (absent means unknown, not exhausted)', () => {
    const store = useUsageStore()
    expect(store.exceededWindow).toBeNull()

    store.weekly = { usedUsd: 0.5, limitUsd: null, resetsAt: null }
    expect(store.exceededWindow).toBeNull()
  })

  it('is null while under the allowance', () => {
    const store = useUsageStore()
    store.weekly = { usedUsd: 0.01, limitUsd: WEEKLY, resetsAt: null }
    expect(store.exceededWindow).toBeNull()
  })

  it('reports the weekly window once the allowance is spent', () => {
    const store = useUsageStore()
    store.weekly = { usedUsd: WEEKLY, limitUsd: WEEKLY, resetsAt: null }
    expect(store.exceededWindow).toBe('week')
  })

  it('stays exhausted past the allowance', () => {
    const store = useUsageStore()
    store.weekly = { usedUsd: WEEKLY + 0.01, limitUsd: WEEKLY, resetsAt: null }
    expect(store.exceededWindow).toBe('week')
  })
})

describe('usage store fetchUsage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    apiMock.get.mockReset()
  })

  it('maps the dollar-denominated payload', async () => {
    apiMock.get.mockResolvedValue({
      data: {
        plan: { id: 'pro', name: 'Pro' },
        windows: {
          weekly: { used_usd: 2.5, limit_usd: 5, resets_at: '2026-07-25T12:00:00Z' },
        },
        plans: [
          { id: 'free', name: 'Free', weekly_usd: 10 },
        ],
      },
    })

    const store = useUsageStore()
    await store.fetchUsage()

    expect(store.plan).toEqual({ id: 'pro', name: 'Pro' })
    expect(store.weekly).toEqual({
      usedUsd: 2.5, limitUsd: 5, resetsAt: '2026-07-25T12:00:00Z',
    })
    expect(store.weeklyPercent).toBe(50)
    expect(store.plans[0].weeklyUsd).toBe(10)
  })

  it('treats a token-denominated payload as unknown rather than dollars', async () => {
    // A backend still on the old contract sends used/limit, not used_usd —
    // reading those as dollars would be wrong by orders of magnitude, so the
    // dollar-suffixed keys must be the only ones that count.
    apiMock.get.mockResolvedValue({
      data: {
        plan: { id: 'free', name: 'Free' },
        windows: { weekly: { used: 2_000_000, limit: 2_000_000, resets_at: null } },
      },
    })

    const store = useUsageStore()
    await store.fetchUsage()

    expect(store.weekly).toEqual({ usedUsd: null, limitUsd: null, resetsAt: null })
    expect(store.weeklyPercent).toBeNull()
    expect(store.exceededWindow).toBeNull()
  })
})

describe('formatUsd', () => {
  it('keeps whole dollars clean and cents precise', () => {
    expect(formatUsd(20)).toBe('$20')
    expect(formatUsd(1.25)).toBe('$1.25')
    expect(formatUsd(0)).toBe('$0')
  })

  it('never rounds a nonzero amount down to zero', () => {
    // "$0.00" would read as "you have used nothing".
    expect(formatUsd(0.0004)).toBe('<$0.01')
  })
})
