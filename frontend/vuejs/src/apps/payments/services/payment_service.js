import axios from 'axios'

class PaymentService {
  constructor() {
    this.apiUrl = import.meta.env.VITE_API_URL || '/api/payments'
    
    // Add request interceptor for auth
    axios.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )
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

  async confirmPayment(paymentIntentId) {
    try {
      const response = await axios.post(`${this.apiUrl}/confirm-payment/`, {
        payment_intent_id: paymentIntentId
      })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async getBalance() {
    try {
      // In development, return mock data if the server is not available
      if (import.meta.env.DEV && !import.meta.env.VITE_API_URL) {
        console.warn('Using mock balance data in development')
        return { balance: 0.00 }
      }

      const response = await axios.get(`${this.apiUrl}/balance/`)
      return response.data
    } catch (error) {
      if (import.meta.env.DEV) {
        console.warn('Failed to fetch balance, using mock data:', error)
        return { balance: 0.00 }
      }
      throw this.handleError(error)
    }
  }

  async getPlans() {
    try {
      const response = await axios.get(`${this.apiUrl}/plans/`)
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

  async getTransactionHistory() {
    try {
      const response = await axios.get(`${this.apiUrl}/transactions/`)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  handleError(error) {
    if (error.response) {
      // Server responded with error
      const message = error.response.data.detail || 
                     error.response.data.message || 
                     error.response.data.error ||
                     this.getErrorMessage(error.response.status)
      return new Error(message)
    }
    if (error.request) {
      // Request made but no response
      if (import.meta.env.DEV) {
        return new Error('Unable to connect to the payment server. Make sure your backend server is running.')
      }
      return new Error('Unable to connect to the payment server. Please try again later.')
    }
    // Something else happened
    return new Error(error.message || 'An unexpected error occurred')
  }

  getErrorMessage(status) {
    const messages = {
      400: 'Invalid request. Please check your input.',
      401: 'Please log in to continue.',
      403: 'You do not have permission to perform this action.',
      404: 'The requested resource was not found.',
      500: 'An internal server error occurred. Please try again later.',
      502: 'The server is temporarily unavailable. Please try again later.',
      503: 'Service unavailable. Please try again later.'
    }
    return messages[status] || 'An error occurred while processing your request'
  }

  async createCheckoutSession(data) {
    try {
      const response = await axios.post(`${this.apiUrl}/create-checkout-session/`, {
        amount: data.amount,
        plan_id: data.plan_id,
        currency: 'usd',
        return_url: `${window.location.origin}/payments/return`
      })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  async getSessionStatus(sessionId) {
    try {
      const response = await axios.get(`${this.apiUrl}/session-status/`, {
        params: { session_id: sessionId }
      })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }
}

export default PaymentService 