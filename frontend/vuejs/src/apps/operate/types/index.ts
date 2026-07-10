/**
 * Types for the Operate module — mirrors the Django Operate app API
 * (backend/django/apps/Operate).
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

export type InvoiceStatus = 'draft' | 'sent' | 'paid' | 'void'

export interface InvoiceLineItem {
  description: string
  quantity: string
  unit_price: string
}

export interface Invoice {
  id: number
  number: string
  customer_name: string
  customer_email: string
  status: InvoiceStatus
  issue_date: string
  due_date: string | null
  line_items: InvoiceLineItem[]
  total: string
  notes: string
  is_overdue: boolean
  sent_at: string | null
  paid_at: string | null
  created_at: string
  updated_at: string
}

export interface InvoicePayload {
  customer_name?: string
  customer_email?: string
  issue_date?: string
  due_date?: string | null
  line_items?: { description: string; quantity: string | number; unit_price: string | number }[]
  notes?: string
}

export type TaskStatus = 'todo' | 'in_progress' | 'done'
export type TaskPriority = 'low' | 'medium' | 'high'

export interface OperationsTask {
  id: number
  title: string
  status: TaskStatus
  priority: TaskPriority
  due_date: string | null
  notes: string
  is_overdue: boolean
  completed_at: string | null
  created_at: string
  updated_at: string
}

export interface TaskPayload {
  title?: string
  status?: TaskStatus
  priority?: TaskPriority
  due_date?: string | null
  notes?: string
}

export interface TaskCounts {
  todo: number
  in_progress: number
  done: number
}

export interface CashflowPoint {
  month: string
  label: string
  income: number
  expenses: number
  net: number
}

export interface DashboardPayload {
  finance: {
    income_30d: number
    expenses_30d: number
    net_30d: number
    income_all_time: number
    expenses_all_time: number
    transactions_total: number
  }
  cashflow: CashflowPoint[]
  invoices: {
    outstanding_total: number
    outstanding_count: number
    overdue_count: number
    draft_count: number
    paid_30d: number
  }
  tasks: {
    open_count: number
    in_progress_count: number
    overdue_count: number
    due_soon_count: number
  }
  marketing: {
    configured: boolean
    contacts_total: number
    contacts_subscribed: number
    campaigns_active: number
    messages_sent_30d: number
    replies_30d: number
  }
  recent_transactions: Transaction[]
  open_invoices: Invoice[]
  upcoming_tasks: OperationsTask[]
}
