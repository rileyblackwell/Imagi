// Define interfaces for the payments store
// These types have been moved from the payments.ts store file

export interface PaymentHistoryItem {
  id: string;
  created_at: string;
  description: string;
  amount: number;
  status: 'completed' | 'pending' | 'failed';
}

export interface Transaction {
  id: string;
  amount: number;
  status: string;
  created_at: string;
  description: string;
}

export interface CreditPackage {
  id: string;
  name: string;
  amount: number;
  price: number;
  description: string;
}

export interface PaymentProcessRequest {
  amount: number;
  paymentMethodId: string;
}

export interface PaymentProcessResponse {
  success: boolean;
  new_balance: number;
  transaction_id?: string;
  message?: string;
}

export interface PaymentStoreState {
  balance: number;
  isLoading: boolean;
  error: string | null;
  paymentHistory: PaymentHistoryItem[];
  isHistoryLoading: boolean;
  transactions: Transaction[];
  packages: CreditPackage[];
} 