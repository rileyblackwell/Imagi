/**
 * Sell workspace helpers.
 *
 * The Tailwind vocabulary lives in `@/shared/styles` — this file only declares
 * which accent Sell wears and re-exports the result, so templates keep reading
 * `ui.card` and `ui.iconTile` while there is one definition of each.
 *
 * Emerald is Sell's colour on the project hub (see businessTools.ts), reserved
 * for identity accents — icon tiles, section badges, selected states. Semantic
 * greens (a paid order) come from `statusTones`, not from here.
 */

import { toolUi } from '@/shared/styles'

export const ui = toolUi('emerald')

/** Sell's accent, for components that need it directly (empty states). */
export const accent = 'emerald' as const

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

/** Format an amount in the smallest currency unit, e.g. 1250 → "$12.50". */
export function formatMoney(cents: number | null | undefined, currency = 'usd'): string {
  const amount = (cents ?? 0) / 100
  try {
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: currency.toUpperCase(),
    }).format(amount)
  } catch {
    return `$${amount.toFixed(2)}`
  }
}
