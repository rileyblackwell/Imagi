// This file helps TypeScript recognize the types directory as a module.
// Merged from index.d.ts
export interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
}

export interface Transaction {
  id: string;
  amount: number;
  status: string;
  transaction_type: string;
  description: string;
  created_at: string;
  stripe_payment_intent_id?: string;
  stripe_checkout_session_id?: string;
}

export interface TransactionHistoryItem {
  id: string;
  date: string;
  amount: number;
  status: string;
  description: string;
}

export interface TransactionFilter {
  status?: string;
  sortBy?: string;
  sortOrder?: string;
}

export interface PaymentIntentData {
  amount: number;
  plan_id?: string;
}

export interface CheckoutSessionData {
  amount: number;
  plan_id?: string;
  currency?: string;
  return_url?: string;
}

export interface PaymentIntent {
  clientSecret: string;
  id?: string;
}

export interface PaymentMethod {
  id: string;
  payment_method_id: string;
  card_brand: string;
  last4: string;
  exp_month: number;
  exp_year: number;
  is_default: boolean;
}

export interface Plan {
  id: string;
  name: string;
  price: number;
  currency: string;
  interval: string;
  credits: number;
}

export interface PaymentResponse {
  success: boolean;
  message?: string;
  transaction?: Transaction;
  error?: string;
}

export interface PaymentIntentRequest {
  amount: number;
  currency?: string;
}

export interface PaymentData {
  amount?: number;
  plan_id?: string;
  success_url?: string;
  cancel_url?: string;
}

export interface BalanceResponse {
  balance: number;
}

export interface TransactionsResponse {
  transactions: Transaction[];
  total_count: number;
}

export interface PaymentIntentResponse {
  clientSecret: string;
  id: string;
}

export interface SessionResponse {
  session_id: string;
  checkout_url: string;
}

export interface SessionStatus {
  status: 'complete' | 'pending';
  payment_status: string;
  credits_added?: number;
}

export interface ErrorMessages {
  [key: number]: string;
}

export interface CreditPackage {
  id: string;
  name: string;
  price: number;
  credits: number;
  amount: number;
  description?: string;
  is_active: boolean;
}

export interface PaymentState {
  balance: number;
  transactions: Transaction[];
  packages: CreditPackage[];
  loading: boolean;
  error: string | null;
}

export interface PaymentDetail {
  label: string;
  value: string | number;
}

export const PAYMENT_STATUS_OPTIONS = [
  { label: 'All Transactions', value: 'all' },
  { label: 'Completed', value: 'completed' },
  { label: 'Pending', value: 'pending' },
  { label: 'Failed', value: 'failed' }
];

export const SORT_OPTIONS = [
  { label: 'Date (Newest First)', value: 'date_desc' },
  { label: 'Date (Oldest First)', value: 'date_asc' },
  { label: 'Amount (Highest First)', value: 'amount_desc' },
  { label: 'Amount (Lowest First)', value: 'amount_asc' }
];

// Re-export all types from models.ts, store.ts, and services.ts for ergonomic imports.
export * from './models';
export * from './store';
export * from './services';