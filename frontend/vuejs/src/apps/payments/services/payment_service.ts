import api from '@/shared/services/api'
import type { AxiosError } from 'axios'
import type {
  TransactionsResponse,
  TransactionFilter,
  PaymentMethod,
  PaymentData,
  SessionResponse,
  SessionStatus,
  ErrorMessages
} from '../types'

/**
 * Billing API client.
 *
 * Only subscriptions are sold, so there is no balance to read, no credits to
 * check or deduct, and no one-time purchase flow. Usage is metered against
 * the plan allowance and read from GET /v1/payments/usage/ by the usage store.
 */
interface IPaymentService {
  apiUrl: string;
  getTransactions(filters?: TransactionFilter): Promise<TransactionsResponse>;
  createCheckoutSession(data: PaymentData): Promise<SessionResponse>;
}

class PaymentService implements IPaymentService {
  apiUrl: string

  constructor() {
    // API client uses relative /api baseURL - proxy handles routing in both dev and production
    // Development: Vite dev server proxies /api/* to localhost:8000
    // Production: Nginx proxies /api/* to backend service
    this.apiUrl = '/v1/payments'; // Kept for interface compatibility
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
      const response = await api.get(`/v1/payments/transactions/${queryString}`)
      return response.data
    } catch (error: any) {
      console.error('Error fetching transactions:', error)
      throw new Error(error.response?.data?.error || error.response?.data?.message || 'Failed to fetch transactions')
    }
  }

  /**
   * Setup customer for future payments
   */
  async setupCustomer(): Promise<any> {
    try {
      const response = await api.post('/v1/payments/setup-customer/')
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
      const response = await api.get('/v1/payments/payment-methods/')
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
      const response = await api.post('/v1/payments/attach-payment-method/', {
        payment_method_id: paymentMethodId
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Create a subscription checkout session for a plan's Stripe lookup_key
   */
  async createCheckoutSession(data: PaymentData): Promise<SessionResponse> {
    try {
      const response = await api.post('/v1/payments/create-checkout-session/', {
        lookup_key: data.lookup_key,
        success_url: data.success_url || window.location.origin + '/payments/success',
        cancel_url: data.cancel_url || window.location.origin + '/payments/cancel'
      })
      return response.data
    } catch (error) {
      throw this.handleError(error as Error)
    }
  }

  /**
   * Create a Stripe Billing Portal session for subscription management
   */
  async createPortalSession(returnUrl?: string): Promise<{ url: string }> {
    try {
      const response = await api.post('/v1/payments/create-portal-session/', {
        return_url: returnUrl || window.location.origin + '/payments/pricing'
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
      const response = await api.get('/v1/payments/session-status/', {
        params: { session_id: sessionId }
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
