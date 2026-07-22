import { defineStore } from 'pinia'
import api from '@/shared/services/api'

/**
 * Plan usage-limit store: the user's plan plus the 5-hour / weekly rolling
 * token windows from GET /api/v1/payments/usage/. This replaces the dollar
 * balance as the workspace's spend surface.
 *
 * All snake_case -> camelCase mapping happens here, and "absent means
 * unknown" is preserved: fields the backend did not report stay null and
 * must never render as 0.
 */

export interface UsageWindow {
  /** Tokens used inside the window; null = unknown, never "free" */
  used: number | null
  /** The plan's token limit for this window; null = unknown */
  limit: number | null
  /** When the oldest counted activity ages out (ISO); null while nothing counts */
  resetsAt: string | null
}

export interface UsagePlan {
  id: string
  name: string
}

/** One entry of the plan registry (for showing what other plans allow). */
export interface UsagePlanLimits {
  id: string
  name: string
  fiveHourTokens: number | null
  weeklyTokens: number | null
}

interface UsageState {
  plan: UsagePlan | null
  plans: UsagePlanLimits[]
  fiveHour: UsageWindow | null
  weekly: UsageWindow | null
  loading: boolean
  error: string | null
}

function toWindow(raw: any): UsageWindow | null {
  if (!raw || typeof raw !== 'object') return null
  return {
    used: typeof raw.used === 'number' ? raw.used : null,
    limit: typeof raw.limit === 'number' ? raw.limit : null,
    resetsAt: typeof raw.resets_at === 'string' ? raw.resets_at : null,
  }
}

/** Compact token count for meters: 850, 12.3k, 2M. */
export function formatCompactTokens(count: number): string {
  if (count >= 1_000_000) {
    const millions = count / 1_000_000
    return `${millions >= 10 ? Math.round(millions) : Math.round(millions * 10) / 10}M`
  }
  if (count >= 1_000) {
    const thousands = count / 1_000
    return `${thousands >= 10 ? Math.round(thousands) : Math.round(thousands * 10) / 10}k`
  }
  return String(count)
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
    /** Percent of the 5-hour window used (0-100), null while unknown. */
    fiveHourPercent(state): number | null {
      const w = state.fiveHour
      if (!w || w.used === null || w.limit === null || w.limit <= 0) return null
      return Math.min(100, Math.round((w.used / w.limit) * 100))
    },

    /** Percent of the weekly window used (0-100), null while unknown. */
    weeklyPercent(state): number | null {
      const w = state.weekly
      if (!w || w.used === null || w.limit === null || w.limit <= 0) return null
      return Math.min(100, Math.round((w.used / w.limit) * 100))
    },

    /** The first exhausted window ('5h' before 'week', matching the backend
     *  check order), or null while under both limits. Unknown data never
     *  reports exhausted (absent means unknown, not over-limit). */
    exceededWindow(state): '5h' | 'week' | null {
      const over = (w: UsageWindow | null) =>
        !!w && w.used !== null && w.limit !== null && w.limit > 0 && w.used >= w.limit
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
              fiveHourTokens: typeof p?.five_hour_tokens === 'number' ? p.five_hour_tokens : null,
              weeklyTokens: typeof p?.weekly_tokens === 'number' ? p.weekly_tokens : null,
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
