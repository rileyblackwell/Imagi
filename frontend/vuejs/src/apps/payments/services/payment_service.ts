import axios from 'axios'
import type { AxiosError } from 'axios'
import type { 
  PaymentIntentRequest, 
  PaymentIntent, 
  BalanceResponse, 
  TransactionsResponse, 
  TransactionFilter,
  PaymentMethod,
  Plan,
  TransactionHistoryItem,
  PaymentData,
  SessionResponse,
  SessionStatus,
  ErrorMessages 
} from '../types'

interface IPaymentService {
  apiUrl: string;
  createPaymentIntent(data: PaymentIntentRequest): Promise<PaymentIntent>;
  getBalance(): Promise<BalanceResponse>;
  getTransactions(filters?: TransactionFilter): Promise<TransactionsResponse>;
  // Additional method signatures...
}

class PaymentService implements IPaymentService {
  apiUrl: string
  private apiBaseUrl: string

  constructor() {
    this.apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'
    this.apiUrl = this.apiBaseUrl + '/payments'
    
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

  /**
   * Create a payment intent for Stripe
   */
  async createPaymentIntent(data: PaymentIntentRequest): Promise<PaymentIntent> {
    try {
      const response = await axios.post(`${this.apiUrl}/create-intent/`, {
        amount: data.amount,
        currency: data.currency || 'usd'
      })
      return response.data
    } catch (error: any) {
      console.error('Error creating payment intent:', error)
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to create payment intent')
    }
  }

  /**
   * Get the user's current balance
   */
  async getBalance(): Promise<BalanceResponse> {
    try {
      const response = await axios.get(`${this.apiUrl}/balance/`)
      return response.data
    } catch (error: any) {
      console.error('Error fetching balance:', error)
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to fetch balance')
    }
  }

  /**
   * Get the user's transaction history (legacy method)
   */
  async getTransactionHistory(): Promise<TransactionHistoryItem[]> {
    try {
      // Use the history endpoint based on our backend implementation
      const response = await axios.get(`${this.apiUrl}/history/`)
      return response.data.payments || []
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Get the user's transaction history with filtering
   */
  async getTransactions(filters?: TransactionFilter): Promise<TransactionsResponse> {
    try {
      // Build query parameters
      const params = new URLSearchParams()
      if (filters?.status) params.append('status', filters.status)
      if (filters?.sortBy) params.append('sort_by', filters.sortBy)
      if (filters?.sortOrder) params.append('sort_order', filters.sortOrder)
      
      const queryString = params.toString() ? `?${params.toString()}` : ''
      const response = await axios.get(`${this.apiUrl}/transactions/${queryString}`)
      return response.data
    } catch (error: any) {
      console.error('Error fetching transactions:', error)
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to fetch transactions')
    }
  }

  /**
   * Get a specific transaction by ID
   */
  async getTransaction(id: string) {
    try {
      const response = await axios.get(`${this.apiUrl}/transactions/${id}/`)
      return response.data
    } catch (error: any) {
      console.error(`Error fetching transaction ${id}:`, error)
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to fetch transaction')
    }
  }

  /**
   * Process payment directly
   */
  async processPayment(amount: number, paymentMethodId: string): Promise<any> {
    try {
      const response = await axios.post(`${this.apiUrl}/process/`, {
        amount,
        payment_method_id: paymentMethodId
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Confirm payment after intent is created
   */
  async confirmPayment(paymentIntentId: string): Promise<any> {
    try {
      const response = await axios.post(`${this.apiUrl}/confirm-payment/`, {
        payment_intent_id: paymentIntentId
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Verify a payment was successful
   */
  async verifyPayment(paymentIntentId: string): Promise<any> {
    try {
      const response = await axios.post(`${this.apiUrl}/verify/`, { 
        payment_intent_id: paymentIntentId 
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Setup a customer for future payments
   */
  async setupCustomer(): Promise<any> {
    try {
      const response = await axios.post(`${this.apiUrl}/setup-customer/`)
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Get saved payment methods
   */
  async getPaymentMethods(): Promise<PaymentMethod[]> {
    try {
      const response = await axios.get(`${this.apiUrl}/payment-methods/`)
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Attach a payment method to customer
   */
  async attachPaymentMethod(paymentMethodId: string): Promise<any> {
    try {
      const response = await axios.post(`${this.apiUrl}/attach-payment-method/`, {
        payment_method_id: paymentMethodId
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Create checkout session for redirect payment flow
   */
  async createCheckoutSession(data: PaymentData): Promise<SessionResponse> {
    try {
      const response = await axios.post(`${this.apiUrl}/create-checkout-session/`, {
        amount: data.amount,
        plan_id: data.plan_id,
        success_url: data.success_url || window.location.origin + '/payments/success',
        cancel_url: data.cancel_url || window.location.origin + '/payments/cancel'
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Get payment session status
   */
  async getSessionStatus(sessionId: string): Promise<SessionStatus> {
    try {
      const response = await axios.get(`${this.apiUrl}/session-status/`, {
        params: { session_id: sessionId }
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Get available subscription plans
   */
  async getPlans(): Promise<Plan[]> {
    try {
      const response = await axios.get(`${this.apiUrl}/plans/`)
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Get available credit packages
   */
  async getPackages(): Promise<any[]> {
    try {
      const response = await axios.get(`${this.apiUrl}/packages/`)
      return response.data.packages || []
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Verify a webhook event from Stripe
   */
  async verifyWebhook(eventId: string) {
    try {
      const response = await axios.post(`${this.apiUrl}/verify-webhook/`, {
        event_id: eventId
      })
      return response.data
    } catch (error: any) {
      console.error('Error verifying webhook:', error)
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to verify webhook')
    }
  }

  /**
   * Check if user has sufficient credits
   */
  async checkCredits(requiredCredits: number): Promise<any> {
    try {
      const response = await axios.post(`${this.apiUrl}/check-credits/`, {
        required_credits: requiredCredits
      })
      return response.data
    } catch (error: any) {
      console.error('Error checking credits:', error)
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to check credits')
    }
  }

  /**
   * Deduct credits from the user's balance
   */
  async deductCredits(credits: number, description?: string): Promise<any> {
    try {
      const response = await axios.post(`${this.apiUrl}/deduct-credits/`, {
        credits,
        description
      })
      return response.data
    } catch (error: any) {
      console.error('Error deducting credits:', error)
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to deduct credits')
    }
  }

  /**
   * Handle API errors with better messaging
   */
  handleError(error: AxiosError | Error): Error {
    // If it's an axios error with a response
    if ('isAxiosError' in error && error.isAxiosError && error.response) {
      const status = error.response.status
      const data = error.response.data as any

      // Try to get a meaningful error message
      const message = data?.message || data?.error || this.getErrorMessageByStatus(status)
      return new Error(message)
    }
    
    // If it's a network error or other non-response error
    return error instanceof Error ? error : new Error('An unknown error occurred')
  }

  /**
   * Get a user-friendly error message based on HTTP status code
   */
  private getErrorMessageByStatus(status: number): string {
    const errorMessages: ErrorMessages = {
      400: 'Bad Request: The payment information provided is invalid.',
      401: 'Unauthorized: Please log in to make a payment.',
      403: 'Forbidden: You do not have permission to perform this action.',
      404: 'Not Found: The requested payment resource was not found.',
      500: 'Server Error: An error occurred while processing your payment. Please try again later.',
      502: 'Server Error: The payment service is temporarily unavailable.',
      503: 'Server Error: The payment service is currently unavailable. Please try again later.',
      504: 'Server Error: The payment request timed out. Please try again.'
    }

    return errorMessages[status as keyof ErrorMessages] || 'An error occurred during the payment process.'
  }
}

export default PaymentService 