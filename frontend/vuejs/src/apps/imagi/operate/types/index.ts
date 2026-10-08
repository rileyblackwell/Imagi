/**
 * Types for the Operate module — mirrors the Django Operate app API
 * (backend/django/apps/Imagi/Operate).
 */

export type TransactionKind = 'income' | 'expense'

export type TransactionCategory =
  | 'sales'
  | 'services'
  | 'other_income'
  | 'supplies'
  | 'software'
  | 'marketing'
  | 'payroll'
  | 'rent'
  | 'utilities'
  | 'fees'
  | 'taxes'
  | 'other_expense'

export const INCOME_CATEGORIES: { value: TransactionCategory; label: string }[] = [
  { value: 'sales', label: 'Sales' },
  { value: 'services', label: 'Services' },
  { value: 'other_income', label: 'Other income' },
]

export const EXPENSE_CATEGORIES: { value: TransactionCategory; label: string }[] = [
  { value: 'supplies', label: 'Supplies' },
  { value: 'software', label: 'Software & tools' },
  { value: 'marketing', label: 'Marketing' },
  { value: 'payroll', label: 'Payroll' },
  { value: 'rent', label: 'Rent' },
  { value: 'utilities', label: 'Utilities' },
  { value: 'fees', label: 'Fees' },
  { value: 'taxes', label: 'Taxes' },
  { value: 'other_expense', label: 'Other expense' },
]

export const CATEGORY_LABELS: Record<TransactionCategory, string> = Object.fromEntries(
  [...INCOME_CATEGORIES, ...EXPENSE_CATEGORIES].map(c => [c.value, c.label])
) as Record<TransactionCategory, string>

export interface Transaction {
  id: number
  kind: TransactionKind
  category: TransactionCategory
  description: string
  /** DRF renders decimals as strings, e.g. "125.50". */
  amount: string
  occurred_on: string
  notes: string
  invoice_id: number | null
  invoice_number: string
  created_at: string
  updated_at: string
}

export interface TransactionPayload {
  kind?: TransactionKind
  category?: TransactionCategory
  description?: string
  amount?: string
  occurred_on?: string
  notes?: string
}

export interface LedgerSummary {
  income: number
  expenses: number
  net: number
}

export interface CashflowPoint {
  month: string
  label: string
  income: number
  expenses: number
  net: number
}

/** The app half: is it up, how fast, who visits. */
export interface AppSummary {
  live_url: string
  site_key: string
  /** The last check is old enough that opening the dashboard should re-check. */
  check_stale: boolean
  status: {
    is_up: boolean
    checked_at: string
    status_code: number | null
    response_ms: number | null
    error: string
  } | null
  uptime: { percent: number | null; checks: number }
  response_ms: { latest: number | null; median: number | null }
  traffic: {
    visitors: number
    page_views: number
    daily: { date: string; label: string; visitors: number }[]
  }
}

/** The business half: revenue, expenses, profit. */
export interface BusinessSummary {
  currency: string
  sell_connected: boolean
  has_ledger: boolean
  revenue_30d: number
  revenue_sell_30d: number
  revenue_recorded_30d: number
  expenses_30d: number
  profit_30d: number
  /** Month by month; `income` is revenue (Sell plus recorded income). */
  monthly: CashflowPoint[]
}

export interface DashboardPayload {
  app: AppSummary
  business: BusinessSummary
}

export interface AppMonitor {
  live_url: string
  site_key: string
  updated_at: string
}
