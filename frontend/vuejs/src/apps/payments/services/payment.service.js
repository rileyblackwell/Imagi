import axios from 'axios'
import { API_URL } from '@/core/config'

class PaymentService {
  async createPaymentIntent(amount) {
    try {
      const response = await axios.post(`${API_URL}/payments/create-intent/`, { amount })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async getBalance() {
    try {
      const response = await axios.get(`${API_URL}/payments/get-balance/`)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async getUsagePricing() {
    try {
      const response = await axios.get(`${API_URL}/payments/usage-pricing/`)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async confirmPayment(paymentIntentId) {
    try {
      const response = await axios.post(`${API_URL}/payments/confirm/`, {
        payment_intent_id: paymentIntentId
      })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  handleError(error) {
    if (error.response) {
      const message = error.response.data.detail || error.response.data.message || 'Payment error occurred'
      return new Error(message)
    } else if (error.request) {
      return new Error('No response from payment server')
    } else {
      return new Error('Error setting up payment request')
    }
  }

  // Helper method to format amount
  formatAmount(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  // Validate payment amount
  validateAmount(amount) {
    const numAmount = Number(amount)
    if (isNaN(numAmount)) {
      throw new Error('Invalid amount')
    }
    if (numAmount < 10) {
      throw new Error('Minimum amount is $10.00')
    }
    if (numAmount > 100) {
      throw new Error('Maximum amount is $100.00')
    }
    return true
  }
} 