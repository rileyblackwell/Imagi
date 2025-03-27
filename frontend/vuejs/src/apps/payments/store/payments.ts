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
import { useBalanceStore } from '@/shared/stores/balance'

// Constants
const BALANCE_REFRESH_INTERVAL = 60000; // 60 seconds
const TRANSACTIONS_CACHE_TIMEOUT = 5000; // 5 seconds

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
    isAutoRefreshEnabled: false, // Disable auto-refresh by default
    lastTransactionsFetch: 0,
    isTransactionsFetching: false,
    lastPackagesFetch: 0
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
      // Use the global balance store for managing balance
      const balanceStore = useBalanceStore();
      await balanceStore.initBalance(); // Initialize only once at startup
      
      // Sync local state with global state
      this.balance = balanceStore.balance;
      this.userCredits = balanceStore.balance;
      this.lastUpdated = balanceStore.lastUpdated;
      
      // Don't auto-refresh balance - only fetch when needed
      balanceStore.stopAutoRefresh();
      
      // Fetch other payment-specific data
      await this.fetchTransactions();
      await this.fetchPackages();
    },
    
    // Start auto-refresh of balance
    startBalanceAutoRefresh(): void {
      // Delegate to global balance store
      const balanceStore = useBalanceStore();
      balanceStore.startAutoRefresh(BALANCE_REFRESH_INTERVAL);
    },
    
    // Stop auto-refresh
    stopBalanceAutoRefresh(): void {
      // Delegate to global balance store
      const balanceStore = useBalanceStore();
      balanceStore.stopAutoRefresh();
    },
    
    // Toggle auto-refresh setting
    toggleAutoRefresh(enabled: boolean): void {
      this.isAutoRefreshEnabled = enabled;
      
      // Delegate to global balance store
      const balanceStore = useBalanceStore();
      balanceStore.toggleAutoRefresh(enabled);
    },
    
    // Fetch user's current balance
    async fetchBalance(showLoading: boolean = true, force: boolean = false): Promise<void> {
      if (showLoading) {
        this.isLoading = true;
      }
      this.error = null;
      
      try {
        // Use global balance store
        const balanceStore = useBalanceStore();
        await balanceStore.fetchBalance(false, force); // Only force refresh when explicitly requested
        
        // Sync local state with global state
        this.balance = balanceStore.balance;
        this.userCredits = balanceStore.balance;
        this.lastUpdated = balanceStore.lastUpdated;
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
      return this.fetchBalance(true, false);
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
      // Check if we have a recent fetch within cache timeout
      const now = Date.now();
      if (
        this.lastTransactionsFetch > 0 && 
        now - this.lastTransactionsFetch < TRANSACTIONS_CACHE_TIMEOUT &&
        this.transactions.length > 0
      ) {
        return;
      }
      
      // If already fetching, don't duplicate the request
      if (this.isTransactionsFetching) {
        return;
      }
      
      this.isHistoryLoading = true;
      this.isTransactionsFetching = true;
      
      try {
        const response = await axios.get<{ transactions: Transaction[] }>('/api/v1/payments/transactions/')
        this.transactions = response.data.transactions;
        this.lastTransactionsFetch = now;
      } catch (error) {
        console.error('Failed to fetch transactions:', error);
      } finally {
        this.isHistoryLoading = false;
        this.isTransactionsFetching = false;
      }
    },
    
    // Process a payment
    async processPayment({ amount, paymentMethodId, saveCard }: PaymentProcessRequest): Promise<PaymentProcessResponse> {
      this.isLoading = true;
      this.error = null;
      
      try {
        // Mark that a transaction is in progress in the balance store
        const balanceStore = useBalanceStore();
        balanceStore.beginTransaction();
        
        const response = await axios.post<PaymentProcessResponse>('/api/v1/payments/process/', {
          amount,
          paymentMethodId,
          saveCard
        });
        
        // Update global balance store
        if (response.data.new_balance !== undefined) {
          balanceStore.updateBalance(response.data.new_balance);
          
          // Sync local state with global state
          this.balance = response.data.new_balance;
          this.userCredits = response.data.new_balance;
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
      // Use simple object-level caching with a 5-second timeout
      const now = Date.now();
      if (
        this.lastPackagesFetch > 0 && 
        now - this.lastPackagesFetch < TRANSACTIONS_CACHE_TIMEOUT &&
        this.packages.length > 0
      ) {
        return;
      }
      
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await axios.get<{ packages: CreditPackage[] }>('/api/v1/payments/packages/')
        // Ensure all packages have a description field to match the type
        this.packages = response.data.packages.map(pkg => ({
          ...pkg,
          description: pkg.description || 'Credit package' // Provide default description if missing
        }));
        this.lastPackagesFetch = now;
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