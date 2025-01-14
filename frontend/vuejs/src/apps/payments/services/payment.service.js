import axios from 'axios'
import config from '@/shared/config'

class PaymentService {
  constructor() {
    this.apiUrl = '/api/payments'
  }

  async createPaymentIntent(amount) {
    try {
      const response = await axios.post(`${this.apiUrl}/create-payment-intent/`, { amount })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async getBalance() {
    try {
      const response = await axios.get(`${this.apiUrl}/get-balance/`)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async getTransactions() {
    try {
      const response = await axios.get(`${this.apiUrl}/transactions/`)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async getCreditPackages() {
    try {
      const response = await axios.get(`${this.apiUrl}/packages/`)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async purchaseCredits(packageId) {
    try {
      const response = await axios.post(`${this.apiUrl}/purchase/`, { package_id: packageId })
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

export default new PaymentService() 