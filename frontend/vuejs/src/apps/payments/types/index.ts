export interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
}

export interface Transaction {
  id: string;
  date: string;
  created_at: string;
  amount: number;
  description: string;
  status: 'completed' | 'pending' | 'failed';
  paymentMethod?: string;
  reference?: string;
}

export interface TransactionHistoryItem {
  id: string;
  amount: number;
  status: string;
  created_at: string;
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
  id: string;
  clientSecret: string;
  amount: number;
  status: string;
  created: number;
}

export interface PaymentMethod {
  id: string;
  type: string;
  card?: {
    brand: string;
    last4: string;
    exp_month: number;
    exp_year: number;
  };
  isDefault?: boolean;
}

export interface Plan {
  id: string;
  name: string;
  amount: number;
  currency: string;
  interval: string;
  description: string;
  features?: string[];
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
  amount: number;
  plan_id?: string;
  success_url?: string;
  cancel_url?: string;
  return_url?: string;
}

export interface BalanceResponse {
  balance: number;
  lastUpdated?: string;
}

export interface TransactionsResponse {
  transactions: Transaction[];
  total: number;
}

export interface PaymentIntentResponse {
  clientSecret: string;
  id: string;
}

export interface SessionResponse {
  id: string;
  url: string;
}

export interface SessionStatus {
  status: 'open' | 'complete' | 'expired';
  payment_status?: 'paid' | 'unpaid';
}

export interface ErrorMessages {
  [key: number]: string;
}

export interface CreditPackage {
  id: string;
  name: string;
  amount: number;
  price: number;
  description: string;
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

// Re-export all store types
export * from './store.types'; 