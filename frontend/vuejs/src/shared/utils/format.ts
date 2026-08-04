/**
 * Display formatting shared across the product.
 *
 * Only genuinely-shared formatters live here. The money formatters stay in
 * their own tools on purpose: Sell counts in the smallest currency unit
 * (Stripe's cents) and Operate in decimal strings (DRF's DecimalField), so a
 * single `formatMoney` would have to guess which, and guessing wrong shows a
 * customer the wrong number.
 */

/** An ISO timestamp for display, e.g. "Jul 10, 3:42 PM". */
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

/** An ISO date (yyyy-mm-dd) for display, e.g. "Jul 10, 2026". */
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

/** Today as yyyy-mm-dd in the user's timezone, for date inputs. */
export function todayISO(): string {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${now.getFullYear()}-${month}-${day}`
}
