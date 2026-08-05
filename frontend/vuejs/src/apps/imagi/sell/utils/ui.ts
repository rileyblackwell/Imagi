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

// Shared display formatters, re-exported so this module stays the single
// import for everything a view in this tool needs.
export { formatDateTime } from '@/shared/utils'
