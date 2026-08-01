import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

const apiMock = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('@/shared/services/api', () => ({
  default: apiMock,
}))

import { useUsageStore, formatUsd } from '@/shared/stores/usage'

// Free-plan allowances: $2.50/week -> $0.50 per 5 hours.
const FIVE_HOUR = 0.5
const WEEKLY = 2.5

describe('usage store exceededWindow', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    apiMock.get.mockReset()
  })

  it('is null while nothing is known (absent means unknown, not exhausted)', () => {
    const store = useUsageStore()
    expect(store.exceededWindow).toBeNull()

    store.fiveHour = { usedUsd: null, limitUsd: FIVE_HOUR, resetsAt: null }
    store.weekly = { usedUsd: 0.5, limitUsd: null, resetsAt: null }
    expect(store.exceededWindow).toBeNull()
  })

  it('is null while under both allowances', () => {
    const store = useUsageStore()
    store.fiveHour = { usedUsd: 0.01, limitUsd: FIVE_HOUR, resetsAt: null }
    store.weekly = { usedUsd: 0.01, limitUsd: WEEKLY, resetsAt: null }
    expect(store.exceededWindow).toBeNull()
  })

  it('reports the five-hour window first, matching the backend check order', () => {
    const store = useUsageStore()
    store.fiveHour = { usedUsd: FIVE_HOUR, limitUsd: FIVE_HOUR, resetsAt: null }
    store.weekly = { usedUsd: WEEKLY, limitUsd: WEEKLY, resetsAt: null }
    expect(store.exceededWindow).toBe('5h')
  })

  it('reports the weekly window when only it is exhausted', () => {
    const store = useUsageStore()
    store.fiveHour = { usedUsd: 0.01, limitUsd: FIVE_HOUR, resetsAt: null }
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
          five_hour: { used_usd: 0.4, limit_usd: 1, resets_at: '2026-07-25T12:00:00Z' },
          weekly: { used_usd: 2.5, limit_usd: 5, resets_at: null },
        },
        plans: [
          { id: 'free', name: 'Free', weekly_usd: 2.5, five_hour_usd: 0.5 },
        ],
      },
    })

    const store = useUsageStore()
    await store.fetchUsage()

    expect(store.plan).toEqual({ id: 'pro', name: 'Pro' })
    expect(store.fiveHour).toEqual({
      usedUsd: 0.4, limitUsd: 1, resetsAt: '2026-07-25T12:00:00Z',
    })
    expect(store.fiveHourPercent).toBe(40)
    expect(store.weeklyPercent).toBe(50)
    expect(store.plans[0].fiveHourUsd).toBe(0.5)
  })

  it('treats a token-denominated payload as unknown rather than dollars', async () => {
    // A backend still on the old contract sends used/limit, not used_usd —
    // reading those as dollars would be wrong by orders of magnitude, so the
    // dollar-suffixed keys must be the only ones that count.
    apiMock.get.mockResolvedValue({
      data: {
        plan: { id: 'free', name: 'Free' },
        windows: { five_hour: { used: 2_000_000, limit: 2_000_000, resets_at: null } },
      },
    })

    const store = useUsageStore()
    await store.fetchUsage()

    expect(store.fiveHour).toEqual({ usedUsd: null, limitUsd: null, resetsAt: null })
    expect(store.fiveHourPercent).toBeNull()
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
