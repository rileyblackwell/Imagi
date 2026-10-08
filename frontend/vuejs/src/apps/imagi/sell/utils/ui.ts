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

/** "$12.00 / month", "$1.00 per 1,000 messages", "$30.00". */
export function describePrice(
  price: { price_cents: number; billing_interval: string; usage_unit_count?: number; usage_unit_label?: string },
  currency = 'usd',
): string {
  const amount = formatMoney(price.price_cents, currency)
  switch (price.billing_interval) {
    case 'month': return `${amount} / month`
    case 'year': return `${amount} / year`
    case 'usage': {
      const count = price.usage_unit_count ?? 1
      const unit = price.usage_unit_label || 'unit'
      return count > 1 ? `${amount} per ${count.toLocaleString()} ${unit}s` : `${amount} per ${unit}`
    }
    default: return amount
  }
}

/** The console's three ways to charge, in its order. */
export const paymentModels = [
  {
    key: 'one_time',
    title: 'One-time payments',
    body: 'Customers pay once for a product or service.',
    examples: 'courses, merch and bookings',
    page: '/store',
  },
  {
    key: 'subscription',
    title: 'Subscriptions',
    body: 'Customers pay every month or year until they cancel.',
    examples: 'memberships and SaaS plans',
    page: '/pricing',
  },
  {
    key: 'usage',
    title: 'Pay as you go',
    body: 'Customers pay each month for what they used.',
    examples: 'API calls, messages and credits',
    page: '/pricing',
  },
] as const

// Shared display formatters, re-exported so this module stays the single
// import for everything a view in this tool needs.
export { formatDateTime } from '@/shared/utils'
