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
    return [
      {
        id: 'starter',
        name: 'Starter Package',
        amount: 10,
        credits: 100,
        features: [
          'Build simple web applications',
          'Basic AI assistance',
          '30-day validity'
        ]
      },
      {
        id: 'pro',
        name: 'Pro Package',
        amount: 25,
        credits: 300,
        popular: true,
        features: [
          'Build complex applications',
          'Advanced AI features',
          '60-day validity',
          'Priority support'
        ]
      },
      {
        id: 'enterprise',
        name: 'Enterprise Package',
        amount: 50,
        credits: 1000,
        features: [
          'Unlimited application complexity',
          'Premium AI features',
          '90-day validity',
          '24/7 priority support',
          'Custom solutions'
        ]
      }
    ]
  }

  async purchaseCredits(packageId) {
    const packages = await this.getCreditPackages()
    const selectedPackage = packages.find(p => p.id === packageId)
    if (!selectedPackage) {
      throw new Error('Invalid package selected')
    }

    try {
      const { clientSecret } = await this.createPaymentIntent(selectedPackage.amount)
      return {
        clientSecret,
        package: selectedPackage
      }
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