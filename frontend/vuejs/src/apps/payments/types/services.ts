import type { AxiosError, AxiosResponse } from 'axios'

// Payment related types
export interface PaymentIntent {
  id: string
  client_secret: string
  status: string
  amount: number
}

export interface PaymentData {
  amount: number
  plan_id?: string
  currency?: string
}

export interface BalanceResponse {
  balance: number
}

export interface Plan {
  id: string
  name: string
  description: string
  amount: number
  features: string[]
}

export interface PaymentMethod {
  id: string
  card: {
    brand: string
    last4: string
    exp_month: number
    exp_year: number
  }
}

export interface TransactionHistoryItem {
  id: string
  amount: number
  status: string
  created: string
  type: string
  description: string
}

export interface SessionResponse {
  id: string
  url: string
}

export interface SessionStatus {
  status: string
  payment_status?: string
}

export interface ErrorMessages {
  [key: number]: string
}

// Payment service interfaces
export interface IPaymentService {
  apiUrl: string
  createPaymentIntent(data: PaymentData): Promise<PaymentIntent>
  confirmPayment(paymentIntentId: string): Promise<any>
  getBalance(): Promise<BalanceResponse>
  getPlans(): Promise<Plan[]>
  verifyPayment(paymentIntentId: string): Promise<any>
  setupCustomer(): Promise<any>
  getPaymentMethods(): Promise<PaymentMethod[]>
  attachPaymentMethod(paymentMethodId: string): Promise<any>
  getTransactionHistory(): Promise<TransactionHistoryItem[]>
  handleError(error: AxiosError | Error): Error
  getErrorMessage(status: number): string
  createCheckoutSession(data: PaymentData): Promise<SessionResponse>
  getSessionStatus(sessionId: string): Promise<SessionStatus>
} 