// Billing types.
//
// Access is sold as subscriptions with a metered dollar allowance, so there is
// no balance, no credit package, and no one-time purchase flow here. Plan and
// usage types live with the usage store (@/shared/stores/usage).

export interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
}

/** A historical credit purchase. Nothing writes these any more. */
export interface Transaction {
  id: string;
  amount: number;
  status: string;
  transaction_type: string;
  description: string;
  created_at: string;
  stripe_payment_intent_id?: string;
  stripe_checkout_session_id?: string;
  model?: string | null;
  request_type?: string | null;
}

export interface TransactionFilter {
  status?: string;
  sortBy?: string;
  sortOrder?: string;
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

/** A subscription checkout, identified by the plan's Stripe price lookup_key. */
export interface PaymentData {
  lookup_key: string;
  success_url?: string;
  cancel_url?: string;
}

export interface TransactionsResponse {
  transactions: Transaction[];
  total_count: number;
}

export interface SessionResponse {
  session_id: string;
  checkout_url: string;
}

export interface SessionStatus {
  status: 'complete' | 'pending';
  payment_status: string;
  mode?: 'subscription';
}

export interface ErrorMessages {
  [key: number]: string;
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
