/**
 * Sell Service — communication with the Sell app API
 * (/api/v1/sell/projects/:projectId/...).
 */

import api from '@/shared/services/api'
import type {
  AppPaymentsInstallResult,
  AppPaymentsState,
  CheckoutSessionStatus,
  Customer,
  CustomerPayload,
  Order,
  OverviewPayload,
  PaymentLinkResult,
  Product,
  ProductPayload,
  SellSettings,
  SellSettingsPayload,
  Subscription,
  VerifyResult,
} from '../types'

const base = (projectId: number) => `/v1/sell/projects/${projectId}`


const SellService = {
  // -- Settings -------------------------------------------------------------
  async getSettings(projectId: number): Promise<SellSettings> {
    const { data } = await api.get(`${base(projectId)}/settings/`)
    return data.settings
  },

  async saveSettings(projectId: number, payload: SellSettingsPayload): Promise<SellSettings> {
    const { data } = await api.put(`${base(projectId)}/settings/`, payload)
    return data.settings
  },

  async verifyConnection(projectId: number): Promise<VerifyResult> {
    const { data } = await api.post(`${base(projectId)}/settings/verify/`)
    return data
  },

  // -- Stripe Connect -------------------------------------------------------
  /** A Stripe-hosted sign-up link; Stripe sends the owner back to returnPath. */
  async startConnect(projectId: number, returnPath: string): Promise<string> {
    const { data } = await api.post(`${base(projectId)}/connect/start/`, { return_path: returnPath })
    return data.url
  },

  async refreshConnect(projectId: number): Promise<SellSettings> {
    const { data } = await api.post(`${base(projectId)}/connect/refresh/`)
    return data.settings
  },

  async disconnect(projectId: number): Promise<SellSettings> {
    const { data } = await api.post(`${base(projectId)}/connect/disconnect/`)
    return data.settings
  },

  async getServerKey(projectId: number): Promise<string> {
    const { data } = await api.get(`${base(projectId)}/server-key/`)
    return data.server_key
  },

  async rotateServerKey(projectId: number): Promise<{ server_key: string; settings: SellSettings }> {
    const { data } = await api.post(`${base(projectId)}/server-key/`)
    return data
  },

  // -- Overview -------------------------------------------------------------
  async getOverview(projectId: number): Promise<OverviewPayload> {
    const { data } = await api.get(`${base(projectId)}/overview/`)
    return data
  },

  // -- Payments in the user's app (prebuilt pages) --------------------------
  async getAppPayments(projectId: number): Promise<AppPaymentsState> {
    const { data } = await api.get(`${base(projectId)}/app-payments/`)
    return data
  },

  async installAppPayments(projectId: number): Promise<AppPaymentsInstallResult> {
    const { data } = await api.post(`${base(projectId)}/app-payments/install/`)
    return data
  },

  // -- Subscriptions ----------------------------------------------------------
  async listSubscriptions(
    projectId: number,
    params: { status?: string; limit?: number; offset?: number } = {}
  ): Promise<{ subscriptions: Subscription[]; total: number }> {
    const { data } = await api.get(`${base(projectId)}/subscriptions/`, { params })
    return data
  },

  // -- Products -------------------------------------------------------------
  async listProducts(
    projectId: number,
    params: { search?: string; active?: string; limit?: number; offset?: number } = {}
  ): Promise<{ products: Product[]; total: number }> {
    const { data } = await api.get(`${base(projectId)}/products/`, { params })
    return data
  },

  async createProduct(projectId: number, payload: ProductPayload): Promise<Product> {
    const { data } = await api.post(`${base(projectId)}/products/`, payload)
    return data.product
  },

  async updateProduct(projectId: number, productId: number, payload: ProductPayload): Promise<Product> {
    const { data } = await api.patch(`${base(projectId)}/products/${productId}/`, payload)
    return data.product
  },

  async deleteProduct(projectId: number, productId: number): Promise<void> {
    await api.delete(`${base(projectId)}/products/${productId}/`)
  },

  async createPaymentLink(projectId: number, productId: number, quantity = 1): Promise<PaymentLinkResult> {
    const { data } = await api.post(
      `${base(projectId)}/products/${productId}/payment-link/`,
      { quantity }
    )
    return data
  },

  // -- Orders ---------------------------------------------------------------
  async listOrders(
    projectId: number,
    params: { status?: string; limit?: number; offset?: number } = {}
  ): Promise<{ orders: Order[]; total: number }> {
    const { data } = await api.get(`${base(projectId)}/orders/`, { params })
    return data
  },

  async fulfillOrder(projectId: number, orderId: number): Promise<Order> {
    const { data } = await api.post(`${base(projectId)}/orders/${orderId}/fulfill/`)
    return data.order
  },

  async syncOrder(projectId: number, orderId: number): Promise<{ updated: boolean; order: Order }> {
    const { data } = await api.post(`${base(projectId)}/orders/${orderId}/sync/`)
    return data
  },

  // -- Customers ------------------------------------------------------------
  async listCustomers(
    projectId: number,
    params: { search?: string; limit?: number; offset?: number } = {}
  ): Promise<{ customers: Customer[]; total: number }> {
    const { data } = await api.get(`${base(projectId)}/customers/`, { params })
    return data
  },

  async createCustomer(projectId: number, payload: CustomerPayload): Promise<Customer> {
    const { data } = await api.post(`${base(projectId)}/customers/`, payload)
    return data.customer
  },

  async getCustomer(projectId: number, customerId: number): Promise<{ customer: Customer; orders: Order[] }> {
    const { data } = await api.get(`${base(projectId)}/customers/${customerId}/`)
    return data
  },

  async updateCustomer(projectId: number, customerId: number, payload: CustomerPayload): Promise<Customer> {
    const { data } = await api.patch(`${base(projectId)}/customers/${customerId}/`, payload)
    return data.customer
  },

  async deleteCustomer(projectId: number, customerId: number): Promise<void> {
    await api.delete(`${base(projectId)}/customers/${customerId}/`)
  },

  // -- Public storefront (used by the checkout return page) ------------------
  async getSessionStatus(projectId: number, sessionId: string): Promise<CheckoutSessionStatus> {
    const { data } = await api.get(`/v1/sell/storefront/${projectId}/sessions/${sessionId}/`)
    return data
  },
}

export default SellService

// The shared implementation; re-exported so this module stays the one place
// each tool's views import their error helper from.
export { extractError } from '@/shared/utils'
