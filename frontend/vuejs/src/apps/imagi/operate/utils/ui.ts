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

// Shared display formatters, re-exported so this module stays the single
// import for everything a view in this tool needs.
export { formatDateTime, formatDate, todayISO } from '@/shared/utils'
