/**
 * Shared Tailwind class strings for the Operate workspace, so every view
 * uses the same design language as the home page and project hub (crisp
 * cards, blue-950 ink, navy pill buttons, warm orange accent). Keep these
 * as full static strings for the JIT compiler.
 */

export const ui = {
  card: 'crisp-card rounded-2xl bg-white dark:bg-white/[0.05] border border-blue-200/70 dark:border-blue-300/[0.16] transition-colors duration-300',

  label: 'block text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/60 dark:text-blue-100/60 mb-1.5 transition-colors duration-300',

  input: 'w-full px-3.5 py-2.5 rounded-xl bg-white dark:bg-white/[0.06] border border-blue-200/70 dark:border-white/[0.12] text-blue-950 dark:text-white text-sm placeholder-blue-950/40 dark:placeholder-blue-100/30 focus:outline-none focus:ring-2 focus:ring-blue-500/40 dark:focus:ring-blue-300/50 focus:border-blue-400/60 dark:focus:border-blue-300/40 transition-colors duration-200',

  primaryBtn: 'inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-full bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white text-sm font-medium transition-colors duration-200 shadow-[0_1px_2px_rgba(23,37,84,0.2),0_3px_8px_-2px_rgba(23,37,84,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e] disabled:opacity-50 disabled:cursor-not-allowed',

  secondaryBtn: 'inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-full border border-blue-950/[0.14] text-blue-950/80 hover:text-blue-950 hover:border-blue-950/30 hover:bg-blue-950/[0.03] dark:border-white/[0.16] dark:text-blue-100/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06] text-sm font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e] disabled:opacity-50 disabled:cursor-not-allowed',

  dangerBtn: 'inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-full border border-red-200/80 dark:border-red-400/25 text-red-600 dark:text-red-300 hover:bg-red-50 dark:hover:bg-red-500/10 hover:border-red-300 dark:hover:border-red-400/40 text-sm font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e] disabled:opacity-50 disabled:cursor-not-allowed',

  iconTile: 'rounded-xl flex items-center justify-center ring-1 bg-orange-100 dark:bg-orange-400/[0.14] ring-orange-900/[0.08] dark:ring-orange-300/[0.18] text-orange-600 dark:text-orange-300 transition-colors duration-300',

  sectionBadge: 'inline-flex items-center px-3 py-1 rounded-full border border-orange-200/70 dark:border-orange-400/25 bg-orange-50/80 dark:bg-orange-400/10 text-xs font-semibold uppercase tracking-[0.18em] text-orange-700 dark:text-orange-300 transition-colors duration-300',

  errorBox: 'p-3.5 rounded-xl border border-red-200/80 dark:border-red-400/25 bg-red-50/80 dark:bg-red-500/10 text-sm text-red-700 dark:text-red-300',

  infoBox: 'p-3.5 rounded-xl border border-blue-200/80 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-sm text-blue-800 dark:text-blue-200',

  successBox: 'p-3.5 rounded-xl border border-emerald-200/80 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-500/10 text-sm text-emerald-700 dark:text-emerald-300',
}

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
