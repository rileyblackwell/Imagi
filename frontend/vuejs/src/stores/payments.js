import { defineStore } from 'pinia'
import PaymentService from '@/apps/payments/services/payment.service'

export const usePaymentStore = defineStore('payments', {
  state: () => ({
    balance: 0,
    transactions: [],
    packages: [],
    loading: false,
    error: null
  }),

  getters: {
    currentBalance: (state) => state.balance,
    allTransactions: (state) => state.transactions,
    availablePackages: (state) => state.packages,
    isLoading: (state) => state.loading,
    getError: (state) => state.error
  },

  actions: {
    setBalance(balance) {
      this.balance = balance
    },

    setTransactions(transactions) {
      this.transactions = transactions
    },

    setPackages(packages) {
      this.packages = packages
    },

    setLoading(loading) {
      this.loading = loading
    },

    setError(error) {
      this.error = error
    },

    async fetchBalance() {
      this.loading = true
      this.error = null
      
      try {
        const { balance } = await PaymentService.getBalance()
        this.setBalance(balance)
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchTransactions() {
      this.loading = true
      this.error = null
      
      try {
        const transactions = await PaymentService.getTransactions()
        this.setTransactions(transactions)
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchPackages() {
      this.loading = true
      this.error = null
      
      try {
        const packages = await PaymentService.getCreditPackages()
        this.setPackages(packages)
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async purchaseCredits(packageId) {
      this.loading = true
      this.error = null
      
      try {
        await PaymentService.purchaseCredits(packageId)
        await this.fetchBalance()
        await this.fetchTransactions()
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    }
  }
}) 