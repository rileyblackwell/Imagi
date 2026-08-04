/**
 * Operate workspace helpers.
 *
 * The Tailwind vocabulary lives in `@/shared/styles` — this file only declares
 * which accent Operate wears and re-exports the result, so templates keep
 * reading `ui.card` and `ui.iconTile` while there is one definition of each.
 *
 * Amber is Operate's colour on the project hub (see businessTools.ts). The
 * workspace previously used orange, half a step off its own card.
 */

import { toolUi } from '@/shared/styles'

export const ui = toolUi('amber')

/** Operate's accent, for components that need it directly (empty states). */
export const accent = 'amber' as const

/** Format a number or DRF decimal string as currency, e.g. "$1,250.50". */
export function formatMoney(value: number | string | null | undefined, currency = 'usd'): string {
  const amount = typeof value === 'string' ? Number.parseFloat(value) : (value ?? 0)
  if (!Number.isFinite(amount)) return '—'
  return amount.toLocaleString(undefined, {
    style: 'currency',
    currency: currency.toUpperCase(),
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

/** Format an ISO timestamp for display, e.g. "Jul 10, 3:42 PM". */
export function formatDateTime(value: string | null | undefined): string {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

/** Format an ISO date (yyyy-mm-dd) for display, e.g. "Jul 10, 2026". */
export function formatDate(value: string | null | undefined): string {
  if (!value) return '—'
  const date = new Date(`${value}T00:00:00`)
  if (Number.isNaN(date.getTime())) return '—'
  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

/** Today's date as yyyy-mm-dd in the user's local timezone (for date inputs). */
export function todayISO(): string {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${now.getFullYear()}-${month}-${day}`
}
