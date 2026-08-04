/**
 * Marketing workspace helpers.
 *
 * The Tailwind vocabulary lives in `@/shared/styles` — this file only declares
 * which accent Market wears and re-exports the result, so templates keep
 * reading `ui.card` and `ui.iconTile` while there is one definition of each.
 *
 * Violet is Market's colour on the project hub (see businessTools.ts), so it is
 * Market's colour in here too. It used to be blue, which made the workspace
 * indistinguishable from the app's own chrome.
 */

import { toolUi } from '@/shared/styles'

export const ui = toolUi('violet')

/** Market's accent, for components that need it directly (empty states). */
export const accent = 'violet' as const

/** Display metadata for the supported ad platforms. */
export const AD_PROVIDERS = {
  google: {
    label: 'Google Ads',
    icon: 'fab fa-google',
    managerUrl: 'https://ads.google.com/aw/campaigns',
    consoleLabel: 'Google Ads',
  },
  meta: {
    label: 'Meta Ads',
    icon: 'fab fa-meta',
    managerUrl: 'https://adsmanager.facebook.com',
    consoleLabel: 'Meta Ads Manager',
  },
} as const

/** Format a count for stat tiles, e.g. 12400 -> "12.4K". */
export function formatCompactNumber(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—'
  return Intl.NumberFormat(undefined, { notation: 'compact', maximumFractionDigits: 1 }).format(value)
}

/** Format a money amount in the account currency, e.g. "$1,234.56". */
export function formatCurrency(
  value: string | number | null | undefined,
  currency: string | null | undefined
): string {
  if (value === null || value === undefined || value === '') return '—'
  const amount = typeof value === 'number' ? value : parseFloat(value)
  if (Number.isNaN(amount)) return '—'
  try {
    return Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: currency || 'USD',
      maximumFractionDigits: 2,
    }).format(amount)
  } catch {
    // Unknown currency code from the platform — show it verbatim.
    return `${amount.toLocaleString()} ${currency}`
  }
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
