import api, { buildApiUrl } from '@/shared/services/api'
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

  constructor() {
    // ALWAYS use relative URLs with buildApiUrl - proxy handles routing in both dev and production
    // Development: Vite dev server proxies /api/* to VITE_BACKEND_URL
    // Production: Nginx proxies /api/* to backend.railway.internal:8000
    this.apiUrl = '/api/v1/payments'; // Kept for interface compatibility
  }

  /**
   * Create a payment intent for processing
   */
  async createPaymentIntent(data: PaymentIntentRequest): Promise<PaymentIntent> {
    try {
      const response = await api.post(buildApiUrl('/api/v1/payments/create-intent/'), {
        amount: data.amount,
        currency: data.currency || 'usd'
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Get the current user's credit balance
   */
  async getBalance(): Promise<BalanceResponse> {
    try {
      const response = await api.get(buildApiUrl('/api/v1/payments/balance/'))
      return response.data
    } catch (error: any) {
      console.error('Error fetching balance:', error)
      
      // Enhanced error reporting with better context
      if (error.response) {
        console.error(`Balance request failed with status ${error.response.status}:`, error.response.data)
      } else if (error.request) {
        console.error('No response received from balance request')
      } 
      
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to fetch balance')
    }
  }

  /**
   * Get payment history
   */
  async getPaymentHistory(): Promise<TransactionHistoryItem[]> {
    try {
      const response = await api.get(buildApiUrl('/api/v1/payments/history/'))
      return response.data.payments || []
    } catch (error: any) {
      console.error('Error fetching payment history:', error)
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to fetch payment history')
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
      const response = await api.get(buildApiUrl(`/api/v1/payments/transactions/${queryString}`))
      return response.data
    } catch (error: any) {
      console.error('Error fetching transactions:', error)
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to fetch transactions')
    }
  }

  /**
   * Get a specific transaction by ID
   */
  async getTransaction(id: string): Promise<any> {
    try {
      const response = await api.get(buildApiUrl(`/api/v1/payments/transactions/${id}/`))
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Process payment directly
   */
  async processPayment(amount: number, paymentMethodId: string): Promise<any> {
    try {
      const response = await api.post(buildApiUrl('/api/v1/payments/process/'), {
        amount,
        payment_method_id: paymentMethodId
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Confirm a payment intent
   */
  async confirmPayment(paymentIntentId: string, paymentMethodId?: string): Promise<any> {
    try {
      const response = await api.post(buildApiUrl('/api/v1/payments/confirm-payment/'), {
        payment_intent_id: paymentIntentId,
        payment_method_id: paymentMethodId
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }
  
  /**
   * Verify payment status
   */
  async verifyPayment(paymentIntentId: string): Promise<any> {
    try {
      const response = await api.post(buildApiUrl('/api/v1/payments/verify/'), {
        payment_intent_id: paymentIntentId
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Setup customer for future payments
   */
  async setupCustomer(): Promise<any> {
    try {
      const response = await api.post(buildApiUrl('/api/v1/payments/setup-customer/'))
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
      const response = await api.get(buildApiUrl('/api/v1/payments/payment-methods/'))
      return response.data.payment_methods || []
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Attach a payment method to customer
   */
  async attachPaymentMethod(paymentMethodId: string): Promise<any> {
    try {
      const response = await api.post(buildApiUrl('/api/v1/payments/attach-payment-method/'), {
        payment_method_id: paymentMethodId
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Create a checkout session
   */
  async createCheckoutSession(data: PaymentData): Promise<SessionResponse> {
    try {
      const response = await api.post(buildApiUrl('/api/v1/payments/create-checkout-session/'), {
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
   * Get checkout session status
   */
  async getSessionStatus(sessionId: string): Promise<SessionStatus> {
    try {
      const response = await api.get(buildApiUrl('/api/v1/payments/session-status/'), {
        params: { session_id: sessionId }
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Get available plans
   */
  async getPlans(): Promise<Plan[]> {
    try {
      const response = await api.get(buildApiUrl('/api/v1/payments/plans/'))
      return response.data.plans || []
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Get available credit packages
   */
  async getPackages(): Promise<any[]> {
    try {
      const response = await api.get(buildApiUrl('/api/v1/payments/packages/'))
      return response.data.packages || []
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Verify webhook signature
   */
  async verifyWebhook(signature: string, payload: string): Promise<any> {
    try {
      const response = await api.post(buildApiUrl('/api/v1/payments/verify-webhook/'), {
        signature,
        payload
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Check if user has sufficient credits
   */
  async checkCredits(amount: number): Promise<{ hasCredits: boolean; currentBalance: number }> {
    try {
      const response = await api.post(buildApiUrl('/api/v1/payments/check-credits/'), {
        amount
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Deduct credits from user account
   */
  async deductCredits(amount: number, description?: string): Promise<{ success: boolean; newBalance: number }> {
    try {
      const response = await api.post(buildApiUrl('/api/v1/payments/deduct-credits/'), {
        amount,
        description
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
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