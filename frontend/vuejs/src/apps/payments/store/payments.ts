import { defineStore } from 'pinia'
import axios from 'axios'
import type { 
  PaymentHistoryItem, 
  PaymentStoreState, 
  PaymentProcessRequest, 
  PaymentProcessResponse,
  CreditPackage,
  Transaction
} from '../types'

// Constants
const BALANCE_REFRESH_INTERVAL = 60000; // 60 seconds

export const usePaymentsStore = defineStore('payments', {
  state: (): PaymentStoreState => ({
    balance: 0,
    userCredits: 0,
    lastUpdated: null,
    isLoading: false,
    error: null,
    paymentHistory: [],
    isHistoryLoading: false,
    transactions: [],
    packages: [],
    balanceRefreshTimer: null,
    isAutoRefreshEnabled: true
  }),
  
  getters: {
    formattedBalance: (state): string => `$${state.balance.toFixed(2)}`,
    hasError: (state): boolean => !!state.error,
    currentBalance: (state) => state.balance,
    allTransactions: (state) => state.transactions,
    availablePackages: (state) => state.packages,
    formattedLastUpdated: (state) => {
      if (!state.lastUpdated) return '';
      return new Date(state.lastUpdated).toLocaleString();
    }
  },
  
  actions: {
    // Initialize balance and auto-refresh
    async initializePayments(): Promise<void> {
      await this.fetchBalance();
      this.startBalanceAutoRefresh();
    },
    
    // Start auto-refresh of balance
    startBalanceAutoRefresh(): void {
      if (this.balanceRefreshTimer) {
        clearInterval(this.balanceRefreshTimer);
      }
      
      if (this.isAutoRefreshEnabled) {
        this.balanceRefreshTimer = setInterval(() => {
          this.fetchBalance(false); // silent refresh
        }, BALANCE_REFRESH_INTERVAL);
      }
    },
    
    // Stop auto-refresh
    stopBalanceAutoRefresh(): void {
      if (this.balanceRefreshTimer) {
        clearInterval(this.balanceRefreshTimer);
        this.balanceRefreshTimer = null;
      }
    },
    
    // Toggle auto-refresh setting
    toggleAutoRefresh(enabled: boolean): void {
      this.isAutoRefreshEnabled = enabled;
      if (enabled) {
        this.startBalanceAutoRefresh();
      } else {
        this.stopBalanceAutoRefresh();
      }
    },
    
    // Fetch user's current balance
    async fetchBalance(showLoading: boolean = true): Promise<void> {
      if (showLoading) {
        this.isLoading = true;
      }
      this.error = null;
      
      try {
        const response = await axios.get<{ balance: number }>('/api/v1/payments/balance/')
        this.balance = response.data.balance;
        this.userCredits = response.data.balance; // Keep them in sync
        this.lastUpdated = new Date();
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to fetch balance';
        console.error('Failed to fetch balance:', error);
      } finally {
        if (showLoading) {
          this.isLoading = false;
        }
      }
    },
    
    // This method is kept for backward compatibility
    async fetchUserCredits(): Promise<void> {
      return this.fetchBalance();
    },
    
    // Fetch user's payment history
    async fetchPaymentHistory(): Promise<void> {
      this.isHistoryLoading = true;
      
      try {
        const response = await axios.get<{ payments: PaymentHistoryItem[] }>('/api/v1/payments/history/')
        this.paymentHistory = response.data.payments;
      } catch (error) {
        console.error('Failed to fetch payment history:', error);
      } finally {
        this.isHistoryLoading = false;
      }
    },
    
    // Fetch all transactions
    async fetchTransactions(): Promise<void> {
      this.isHistoryLoading = true;
      
      try {
        const response = await axios.get<{ transactions: Transaction[] }>('/api/v1/payments/transactions/')
        this.transactions = response.data.transactions;
      } catch (error) {
        console.error('Failed to fetch transactions:', error);
      } finally {
        this.isHistoryLoading = false;
      }
    },
    
    // Process a payment
    async processPayment({ amount, paymentMethodId, saveCard }: PaymentProcessRequest): Promise<PaymentProcessResponse> {
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await axios.post<PaymentProcessResponse>('/api/v1/payments/process/', {
          amount,
          paymentMethodId,
          saveCard
        });
        
        // Update balance after successful payment
        this.balance = response.data.new_balance;
        
        // Update user credits
        if (response.data.credits_added) {
          this.userCredits = response.data.new_balance; // Update for consistency
          this.lastUpdated = new Date();
        }
        
        // Fetch payment history after successful payment
        this.fetchPaymentHistory();
        this.fetchTransactions();
        
        // Return payment data for further processing
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Payment processing failed';
        console.error('Payment processing failed:', error);
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
    
    // Fetch available credit packages
    async fetchPackages(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await axios.get<{ packages: CreditPackage[] }>('/api/v1/payments/packages/')
        // Ensure all packages have a description field to match the type
        this.packages = response.data.packages.map(pkg => ({
          ...pkg,
          description: pkg.description || 'Credit package' // Provide default description if missing
        }));
      } catch (error: any) {
        this.error = error.response?.data?.message || 'Failed to fetch packages';
        console.error('Failed to fetch credit packages:', error);
      } finally {
        this.isLoading = false;
      }
    },
    
    clearError(): void {
      this.error = null;
    },
    
    // Clean up resources when the store is no longer needed
    onUnmounted(): void {
      this.stopBalanceAutoRefresh();
    }
  }
})

export default usePaymentsStore 