import { defineStore } from 'pinia'
import api from '@/shared/services/api'

/**
 * Plan usage store: the user's plan plus the 5-hour / weekly rolling usage
 * windows from GET /api/v1/payments/usage/.
 *
 * Usage is metered in dollars of model spend, not tokens — a pricier model or
 * a heavier reasoning effort draws the allowance down faster. This is the
 * workspace's only spend surface; there is no dollar balance to top up.
 *
 * All snake_case -> camelCase mapping happens here, and "absent means
 * unknown" is preserved: fields the backend did not report stay null and
 * must never render as 0.
 */

export interface UsageWindow {
  /** Dollars of usage inside the window; null = unknown, never "free" */
  usedUsd: number | null
  /** The plan's dollar allowance for this window; null = unknown */
  limitUsd: number | null
  /** When the oldest counted activity ages out (ISO); null while nothing counts */
  resetsAt: string | null
}

export interface UsagePlan {
  id: string
  name: string
}

/** One entry of the plan registry (for showing what other plans allow).
 *  Only the two enforced windows exist — there is no monthly figure. */
export interface UsagePlanLimits {
  id: string
  name: string
  weeklyUsd: number | null
  fiveHourUsd: number | null
}

interface UsageState {
  plan: UsagePlan | null
  plans: UsagePlanLimits[]
  fiveHour: UsageWindow | null
  weekly: UsageWindow | null
  loading: boolean
  error: string | null
}

function toNumber(value: any): number | null {
  return typeof value === 'number' && !isNaN(value) ? value : null
}

function toWindow(raw: any): UsageWindow | null {
  if (!raw || typeof raw !== 'object') return null
  return {
    usedUsd: toNumber(raw.used_usd),
    limitUsd: toNumber(raw.limit_usd),
    resetsAt: typeof raw.resets_at === 'string' ? raw.resets_at : null,
  }
}

/**
 * Dollar amount for meters and allowances. Whole dollars stay clean ($20),
 * and anything smaller keeps two decimals ($1.25) — but a nonzero amount
 * under a cent shows as "<$0.01" rather than rounding to $0.00, which would
 * read as "you've used nothing".
 */
export function formatUsd(amount: number): string {
  if (amount > 0 && amount < 0.01) return '<$0.01'
  if (Number.isInteger(amount)) return `$${amount}`
  return `$${amount.toFixed(2)}`
}

/** Human wording for a window's reset moment ("3:45 PM" / "Jul 24, 3:45 PM"). */
export function formatResetTime(iso: string | null | undefined): string | null {
  if (!iso) return null
  const date = new Date(iso)
  if (isNaN(date.getTime())) return null
  const time = date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
  const today = new Date()
  const sameDay = date.getFullYear() === today.getFullYear()
    && date.getMonth() === today.getMonth()
    && date.getDate() === today.getDate()
  if (sameDay) return time
  return `${date.toLocaleDateString([], { month: 'short', day: 'numeric' })}, ${time}`
}

export const useUsageStore = defineStore('usage', {
  state: (): UsageState => ({
    plan: null,
    plans: [],
    fiveHour: null,
    weekly: null,
    loading: false,
    error: null,
  }),

  getters: {
    /** Percent of the 5-hour allowance used (0-100), null while unknown. */
    fiveHourPercent(state): number | null {
      const w = state.fiveHour
      if (!w || w.usedUsd === null || w.limitUsd === null || w.limitUsd <= 0) return null
      return Math.min(100, Math.round((w.usedUsd / w.limitUsd) * 100))
    },

    /** Percent of the weekly allowance used (0-100), null while unknown. */
    weeklyPercent(state): number | null {
      const w = state.weekly
      if (!w || w.usedUsd === null || w.limitUsd === null || w.limitUsd <= 0) return null
      return Math.min(100, Math.round((w.usedUsd / w.limitUsd) * 100))
    },

    /** The first exhausted window ('5h' before 'week', matching the backend
     *  check order), or null while under both allowances. Unknown data never
     *  reports exhausted (absent means unknown, not over-limit). */
    exceededWindow(state): '5h' | 'week' | null {
      const over = (w: UsageWindow | null) =>
        !!w && w.usedUsd !== null && w.limitUsd !== null && w.limitUsd > 0
          && w.usedUsd >= w.limitUsd
      if (over(state.fiveHour)) return '5h'
      if (over(state.weekly)) return 'week'
      return null
    },
  },

  actions: {
    /** Refresh plan + windows. Errors land in state.error (and the previous
     *  data stays — stale beats wrongly-zero); callers never need a catch. */
    async fetchUsage() {
      this.loading = true
      this.error = null
      try {
        const response = await api.get('/v1/payments/usage/')
        const data = response.data ?? {}
        this.plan = data.plan && data.plan.id
          ? { id: String(data.plan.id), name: String(data.plan.name ?? data.plan.id) }
          : null
        this.plans = Array.isArray(data.plans)
          ? data.plans.map((p: any): UsagePlanLimits => ({
              id: String(p?.id ?? ''),
              name: String(p?.name ?? p?.id ?? ''),
              weeklyUsd: toNumber(p?.weekly_usd),
              fiveHourUsd: toNumber(p?.five_hour_usd),
            }))
          : []
        this.fiveHour = toWindow(data.windows?.five_hour)
        this.weekly = toWindow(data.windows?.weekly)
      } catch (error: any) {
        console.error('Error fetching usage status:', error)
        this.error = error?.message || 'Failed to fetch usage'
      } finally {
        this.loading = false
      }
    },
  },
})
