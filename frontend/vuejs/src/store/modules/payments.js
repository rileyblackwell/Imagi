import axios from 'axios'

const state = {
  balance: 0,
  transactions: [],
  loading: false,
  error: null,
  checkoutSession: null
}

const mutations = {
  SET_BALANCE(state, balance) {
    state.balance = balance
  },
  
  SET_TRANSACTIONS(state, transactions) {
    state.transactions = transactions
  },
  
  ADD_TRANSACTION(state, transaction) {
    state.transactions.unshift(transaction)
  },
  
  SET_CHECKOUT_SESSION(state, session) {
    state.checkoutSession = session
  },
  
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  
  SET_ERROR(state, error) {
    state.error = error
  }
}

const actions = {
  async fetchBalance({ commit }) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      const response = await axios.get('/api/payments/balance/')
      commit('SET_BALANCE', response.data.balance)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to fetch balance')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async fetchTransactions({ commit }) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      const response = await axios.get('/api/payments/transactions/')
      commit('SET_TRANSACTIONS', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to fetch transactions')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async createCheckoutSession({ commit }, { amount }) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      const response = await axios.post('/api/payments/create-checkout-session/', { amount })
      commit('SET_CHECKOUT_SESSION', response.data)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to create checkout session')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  async handlePaymentSuccess({ commit, dispatch }, { session_id }) {
    try {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      
      const response = await axios.post('/api/payments/payment-success/', { session_id })
      
      // Update balance after successful payment
      await dispatch('fetchBalance')
      
      // Add new transaction
      commit('ADD_TRANSACTION', response.data.transaction)
      
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to process payment')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const getters = {
  currentBalance: state => state.balance,
  allTransactions: state => state.transactions,
  checkoutSession: state => state.checkoutSession,
  loading: state => state.loading,
  error: state => state.error,
  
  recentTransactions: state => {
    return state.transactions.slice(0, 5)
  },
  
  sortedTransactions: state => {
    return [...state.transactions].sort((a, b) => {
      return new Date(b.created_at) - new Date(a.created_at)
    })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
} 