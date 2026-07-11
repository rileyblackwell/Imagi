/**
 * Sell Service — communication with the Sell app API
 * (/api/v1/sell/projects/:projectId/...).
 */

import api from '@/shared/services/api'
import type {
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
  VerifyResult,
} from '../types'

const base = (projectId: number) => `/v1/sell/projects/${projectId}`

/** Pull a readable message out of an axios/DRF error. */
export function extractError(error: unknown, fallback = 'Something went wrong'): string {
  const data = (error as { response?: { data?: unknown } })?.response?.data
  if (typeof data === 'string') return fallback
  if (data && typeof data === 'object') {
    const payload = data as Record<string, unknown>
    if (typeof payload.error === 'string') return payload.error
    if (typeof payload.detail === 'string') return payload.detail
    // DRF field errors: {"field": ["message", ...]}
    for (const [field, value] of Object.entries(payload)) {
      const first = Array.isArray(value) ? value[0] : value
      if (typeof first === 'string') {
        return field === 'non_field_errors' ? first : `${field.replace(/_/g, ' ')}: ${first}`
      }
    }
  }
  const message = (error as { message?: string })?.message
  return message || fallback
}

export const SellService = {
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

  // -- Overview -------------------------------------------------------------
  async getOverview(projectId: number): Promise<OverviewPayload> {
    const { data } = await api.get(`${base(projectId)}/overview/`)
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

  async getOrder(projectId: number, orderId: number): Promise<Order> {
    const { data } = await api.get(`${base(projectId)}/orders/${orderId}/`)
    return data.order
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
