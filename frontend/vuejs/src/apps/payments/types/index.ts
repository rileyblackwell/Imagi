// Billing types.
//
// Imagi has one plan, Free, with a metered weekly dollar allowance, and sells
// nothing: no balance, no credit package, no subscription checkout. Plan and
// usage types live with the usage store (@/shared/stores/usage).

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

export interface TransactionsResponse {
  transactions: Transaction[];
  total_count: number;
}

export interface ErrorMessages {
  [key: number]: string;
}
