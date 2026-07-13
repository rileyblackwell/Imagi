/**
 * Shared Tailwind class strings for the Marketing workspace, so every view
 * uses the same design language as the project hub (crisp cards, blue-950
 * ink, violet accent). Keep these as full static strings for the JIT compiler.
 */

export const ui = {
  card: 'crisp-card rounded-2xl bg-white dark:bg-white/[0.05] border border-blue-200/70 dark:border-blue-300/[0.16] transition-colors duration-300',

  label: 'block text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/60 dark:text-blue-100/60 mb-1.5 transition-colors duration-300',

  input: 'w-full px-3.5 py-2.5 rounded-xl bg-white dark:bg-white/[0.06] border border-blue-200/70 dark:border-white/[0.12] text-blue-950 dark:text-white text-sm placeholder-blue-950/40 dark:placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-violet-400/40 focus:border-violet-300 dark:focus:border-violet-400/40 transition-colors duration-200',

  primaryBtn: 'inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-sm font-medium transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed',

  secondaryBtn: 'inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-white dark:bg-white/[0.06] hover:bg-blue-50 dark:hover:bg-white/[0.1] border border-blue-200/70 dark:border-white/[0.12] text-blue-950 dark:text-white text-sm font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed',

  dangerBtn: 'inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-white dark:bg-white/[0.06] hover:bg-red-50 dark:hover:bg-red-500/10 border border-red-200/80 dark:border-red-400/25 text-red-600 dark:text-red-300 text-sm font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed',

  iconTile: 'rounded-xl flex items-center justify-center border bg-violet-50 dark:bg-violet-400/10 border-violet-200/60 dark:border-violet-400/25 text-violet-600 dark:text-violet-300 transition-colors duration-300',

  sectionBadge: 'inline-flex items-center px-3 py-1 rounded-full border border-violet-200/70 dark:border-violet-400/25 bg-violet-50/80 dark:bg-violet-400/10 text-xs font-semibold uppercase tracking-[0.18em] text-violet-700 dark:text-violet-300 transition-colors duration-300',

  errorBox: 'p-3.5 rounded-xl border border-red-200/80 dark:border-red-400/25 bg-red-50/80 dark:bg-red-500/10 text-sm text-red-700 dark:text-red-300',

  infoBox: 'p-3.5 rounded-xl border border-blue-200/80 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-sm text-blue-800 dark:text-blue-200',

  successBox: 'p-3.5 rounded-xl border border-emerald-200/80 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-500/10 text-sm text-emerald-700 dark:text-emerald-300',
}

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
