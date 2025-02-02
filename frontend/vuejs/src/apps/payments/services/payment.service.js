import axios from 'axios'

class PaymentService {
  constructor() {
    this.apiUrl = '/api/payments'
  }

  async createPaymentIntent(data) {
    try {
      const response = await axios.post(`${this.apiUrl}/create-payment-intent/`, data)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async getBalance() {
    try {
      const response = await axios.get(`${this.apiUrl}/balance/`)
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

  async getCreditPackage(packageId) {
    try {
      const response = await axios.get(`${this.apiUrl}/packages/${packageId}/`)
      return response
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async verifyPayment(paymentIntentId) {
    try {
      const response = await axios.post(`${this.apiUrl}/verify/`, { 
        payment_intent_id: paymentIntentId 
      })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  handleError(error) {
    if (error.response) {
      // Use a more descriptive error message based on the response
      const message = error.response.data.detail || 
                     error.response.data.message || 
                     'An error occurred while processing your request'
      return new Error(message)
    }
    if (error.request) {
      return new Error('Unable to connect to the payment server')
    }
    return new Error('An unexpected error occurred')
  }

  // For development/testing - returns mock packages if API is not available
  async getMockPackages() {
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
}

export default PaymentService 