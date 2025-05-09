// Core domain models for payments

export interface PaymentMethod {
  id: string;
  brand: string;
  last4: string;
  expMonth: number;
  expYear: number;
  isDefault: boolean;
  is_default?: boolean; // for snake_case compatibility
}

export interface CreditPackage {
  id: string;
  name: string;
  credits: number;
  price: number; // in cents
  description?: string;
}

export interface Transaction {
  id: string;
  amount: number;
  date: string | null;
  status: 'pending' | 'completed' | 'failed';
  description?: string | null;
  paymentMethodId?: string | null;
  created_at?: string | null;
  model?: string | null;
  request_type?: string | null;
}

export interface Plan {
  id: string;
  name: string;
  price: number;
  credits: number;
  description?: string;
}
