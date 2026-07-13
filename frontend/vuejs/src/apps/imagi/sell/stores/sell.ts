/**
 * Pinia store for the Sell workspace.
 *
 * Holds the state shared across the sell tabs (settings, products, orders,
 * customers, overview) for the currently open project. The workspace shell
 * calls `setProject()` once the project is resolved from the URL slug;
 * every view then reads `projectId` from here.
 */

import { defineStore } from 'pinia'
import SellService from '../services/sellService'
import type {
  Customer,
  CustomerPayload,
  Order,
  OverviewPayload,
  PaymentLinkResult,
  PaymentTemplate,
  Product,
  ProductPayload,
  SellSettings,
  SellSettingsPayload,
  TemplateInstallResult,
  VerifyResult,
} from '../types'

interface SellState {
  projectId: number | null
  settings: SellSettings | null
  settingsLoading: boolean
  overview: OverviewPayload | null
  overviewLoading: boolean
  templates: PaymentTemplate[]
  templatesLoading: boolean
  products: Product[]
  productsTotal: number
  productsLoading: boolean
  orders: Order[]
  ordersTotal: number
  ordersLoading: boolean
  customers: Customer[]
  customersTotal: number
  customersLoading: boolean
}

export const useSellStore = defineStore('sell', {
  state: (): SellState => ({
    projectId: null,
    settings: null,
    settingsLoading: false,
    overview: null,
    overviewLoading: false,
    templates: [],
    templatesLoading: false,
    products: [],
    productsTotal: 0,
    productsLoading: false,
    orders: [],
    ordersTotal: 0,
    ordersLoading: false,
    customers: [],
    customersTotal: 0,
    customersLoading: false,
  }),

  getters: {
    isConfigured: (state) => Boolean(state.settings?.is_configured),
    currency: (state) => state.settings?.currency || 'usd',
  },

  actions: {
    /** Point the store at a project; clears data when switching projects. */
    setProject(projectId: number) {
      if (this.projectId !== projectId) {
        this.$reset()
        this.projectId = projectId
      }
    },

    requireProject(): number {
      if (this.projectId === null) {
        throw new Error('Sell store has no active project')
      }
      return this.projectId
    },

    // -- Settings -----------------------------------------------------------
    async fetchSettings(): Promise<SellSettings> {
      const projectId = this.requireProject()
      this.settingsLoading = true
      try {
        this.settings = await SellService.getSettings(projectId)
        return this.settings
      } finally {
        this.settingsLoading = false
      }
    },

    async saveSettings(payload: SellSettingsPayload): Promise<SellSettings> {
      const projectId = this.requireProject()
      this.settings = await SellService.saveSettings(projectId, payload)
      return this.settings
    },

    async verifyConnection(): Promise<VerifyResult> {
      const projectId = this.requireProject()
      const result = await SellService.verifyConnection(projectId)
      this.settings = result.settings
      return result
    },

    // -- Overview -----------------------------------------------------------
    async fetchOverview(): Promise<OverviewPayload> {
      const projectId = this.requireProject()
      this.overviewLoading = true
      try {
        this.overview = await SellService.getOverview(projectId)
        return this.overview
      } finally {
        this.overviewLoading = false
      }
    },

    // -- Payment templates ----------------------------------------------------
    async fetchTemplates(): Promise<PaymentTemplate[]> {
      const projectId = this.requireProject()
      this.templatesLoading = true
      try {
        this.templates = await SellService.listTemplates(projectId)
        return this.templates
      } finally {
        this.templatesLoading = false
      }
    },

    async installTemplate(key: string): Promise<TemplateInstallResult> {
      const projectId = this.requireProject()
      const result = await SellService.installTemplate(projectId, key)
      this.templates = result.templates
      return result
    },

    // -- Products -----------------------------------------------------------
    async fetchProducts(params: { search?: string; active?: string; limit?: number; offset?: number } = {}) {
      const projectId = this.requireProject()
      this.productsLoading = true
      try {
        const { products, total } = await SellService.listProducts(projectId, params)
        this.products = products
        this.productsTotal = total
      } finally {
        this.productsLoading = false
      }
    },

    async createProduct(payload: ProductPayload): Promise<Product> {
      return SellService.createProduct(this.requireProject(), payload)
    },

    async updateProduct(productId: number, payload: ProductPayload): Promise<Product> {
      const product = await SellService.updateProduct(this.requireProject(), productId, payload)
      const index = this.products.findIndex(p => p.id === productId)
      if (index !== -1) this.products[index] = product
      return product
    },

    async deleteProduct(productId: number): Promise<void> {
      await SellService.deleteProduct(this.requireProject(), productId)
      this.products = this.products.filter(p => p.id !== productId)
      this.productsTotal = Math.max(this.productsTotal - 1, 0)
    },

    async createPaymentLink(productId: number, quantity = 1): Promise<PaymentLinkResult> {
      return SellService.createPaymentLink(this.requireProject(), productId, quantity)
    },

    // -- Orders -------------------------------------------------------------
    async fetchOrders(params: { status?: string; limit?: number; offset?: number } = {}) {
      const projectId = this.requireProject()
      this.ordersLoading = true
      try {
        const { orders, total } = await SellService.listOrders(projectId, params)
        this.orders = orders
        this.ordersTotal = total
      } finally {
        this.ordersLoading = false
      }
    },

    replaceOrder(order: Order) {
      const index = this.orders.findIndex(o => o.id === order.id)
      if (index !== -1) this.orders[index] = order
    },

    async fulfillOrder(orderId: number): Promise<Order> {
      const order = await SellService.fulfillOrder(this.requireProject(), orderId)
      this.replaceOrder(order)
      return order
    },

    async syncOrder(orderId: number): Promise<{ updated: boolean; order: Order }> {
      const result = await SellService.syncOrder(this.requireProject(), orderId)
      this.replaceOrder(result.order)
      return result
    },

    // -- Customers ----------------------------------------------------------
    async fetchCustomers(params: { search?: string; limit?: number; offset?: number } = {}) {
      const projectId = this.requireProject()
      this.customersLoading = true
      try {
        const { customers, total } = await SellService.listCustomers(projectId, params)
        this.customers = customers
        this.customersTotal = total
      } finally {
        this.customersLoading = false
      }
    },

    async createCustomer(payload: CustomerPayload): Promise<Customer> {
      return SellService.createCustomer(this.requireProject(), payload)
    },

    async getCustomer(customerId: number): Promise<{ customer: Customer; orders: Order[] }> {
      return SellService.getCustomer(this.requireProject(), customerId)
    },

    async updateCustomer(customerId: number, payload: CustomerPayload): Promise<Customer> {
      const customer = await SellService.updateCustomer(this.requireProject(), customerId, payload)
      const index = this.customers.findIndex(c => c.id === customerId)
      if (index !== -1) this.customers[index] = customer
      return customer
    },

    async deleteCustomer(customerId: number): Promise<void> {
      await SellService.deleteCustomer(this.requireProject(), customerId)
      this.customers = this.customers.filter(c => c.id !== customerId)
      this.customersTotal = Math.max(this.customersTotal - 1, 0)
    },
  },
})
