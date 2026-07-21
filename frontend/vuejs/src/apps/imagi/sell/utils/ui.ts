/**
 * Shared Tailwind class strings for the Sell workspace, aligned to the
 * warm-porcelain editorial system defined by the home page: blue-950 ink,
 * navy pill buttons, hairline borders, crisp-card panels. Emerald stays
 * reserved for the Sell tool's identity accents (icon tiles, section badge,
 * selected states — its color in businessTools.ts) and semantic statuses.
 * Keep these as full static strings for the JIT compiler.
 */

export const ui = {
  card: 'crisp-card rounded-2xl bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm border border-blue-200/70 dark:border-blue-300/[0.14] transition-colors duration-300',

  label: 'block text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/70 dark:text-blue-100/55 mb-1.5 transition-colors duration-300',

  input: 'w-full px-3.5 py-2.5 rounded-xl bg-white dark:bg-white/[0.06] border border-blue-950/[0.14] dark:border-white/[0.14] text-blue-950 dark:text-white text-sm placeholder-blue-950/40 dark:placeholder-blue-100/30 focus:outline-none focus:ring-2 focus:ring-blue-500/40 dark:focus:ring-blue-300/50 focus:border-blue-300 dark:focus:border-blue-400/40 transition-colors duration-200',

  primaryBtn: 'inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-full bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white text-sm font-medium transition-colors duration-200 shadow-[0_1px_2px_rgba(23,37,84,0.2),0_3px_8px_-2px_rgba(23,37,84,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e] disabled:opacity-50 disabled:cursor-not-allowed',

  secondaryBtn: 'inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-full border border-blue-950/[0.14] text-blue-950/80 hover:text-blue-950 hover:border-blue-950/30 hover:bg-blue-950/[0.03] dark:border-white/[0.16] dark:text-blue-100/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06] text-sm font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e] disabled:opacity-50 disabled:cursor-not-allowed',

  dangerBtn: 'inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-full border border-red-200/80 dark:border-red-400/25 text-red-600 dark:text-red-300 hover:bg-red-50 dark:hover:bg-red-500/10 hover:border-red-300 dark:hover:border-red-400/40 text-sm font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e] disabled:opacity-50 disabled:cursor-not-allowed',

  iconTile: 'rounded-xl flex items-center justify-center border bg-emerald-50 dark:bg-emerald-400/10 border-emerald-200/60 dark:border-emerald-400/25 text-emerald-600 dark:text-emerald-300 transition-colors duration-300',

  sectionBadge: 'inline-flex items-center px-3.5 py-1.5 rounded-full border border-emerald-200/70 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-400/10 text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700 dark:text-emerald-300 transition-colors duration-300',

  errorBox: 'p-3.5 rounded-xl border border-red-200/80 dark:border-red-400/25 bg-red-50/80 dark:bg-red-500/10 text-sm text-red-700 dark:text-red-300',

  infoBox: 'p-3.5 rounded-xl border border-blue-200/80 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-sm text-blue-800 dark:text-blue-200',

  successBox: 'p-3.5 rounded-xl border border-emerald-200/80 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-500/10 text-sm text-emerald-700 dark:text-emerald-300',
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
