import axios from 'axios'

class PaymentService {
  constructor() {
    this.apiUrl = '/api/payments'
  }

  async createPaymentIntent(data) {
    try {
      const response = await axios.post(`${this.apiUrl}/create-payment-intent/`, {
        amount: data.amount
      })
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

  async setupCustomer() {
    try {
      const response = await axios.post(`${this.apiUrl}/setup-customer/`)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async getPaymentMethods() {
    try {
      const response = await axios.get(`${this.apiUrl}/payment-methods/`)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async attachPaymentMethod(paymentMethodId) {
    try {
      const response = await axios.post(`${this.apiUrl}/attach-payment-method/`, {
        payment_method_id: paymentMethodId
      })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  handleError(error) {
    if (error.response) {
      const message = error.response.data.detail || 
                     error.response.data.message || 
                     error.response.data.error ||
                     'An error occurred while processing your request'
      return new Error(message)
    }
    if (error.request) {
      return new Error('Unable to connect to the payment server')
    }
    return new Error('An unexpected error occurred')
  }

  // Get user's transaction history
  async getTransactionHistory() {
    try {
      const response = await axios.get(`${this.apiUrl}/transactions/`)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }
}

export default PaymentService 