/**
 * Types for the Sell module — mirrors the Django Sell app API
 * (backend/django/apps/Sell).
 */

export interface SellSettings {
  stripe_publishable_key: string
  /** True when a secret key is stored server-side (the key itself is never returned). */
  stripe_secret_key_set: boolean
  /** True when a webhook signing secret is stored server-side. */
  stripe_webhook_secret_set: boolean
  currency: string
  account_name: string
  account_email: string
  last_verified_at: string | null
  is_configured: boolean
  /** Stripe webhook URL to register in the Stripe dashboard; empty when the backend has no public base URL configured. */
  stripe_webhook_url: string
}

export interface SellSettingsPayload {
  stripe_publishable_key?: string
  /** Write-only; omit or send '' to keep the stored key. */
  stripe_secret_key?: string
  /** Write-only; omit or send '' to keep the stored secret. */
  stripe_webhook_secret?: string
  currency?: string
}

export interface VerifyResult {
  verified: boolean
  account_name: string
  account_email: string
  charges_enabled: boolean
  settings: SellSettings
}

export type BillingInterval = 'one_time' | 'month' | 'year'

export interface Product {
  id: number
  name: string
  description: string
  price_cents: number
  image_url: string
  billing_interval: BillingInterval
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ProductPayload {
  name?: string
  description?: string
  price_cents?: number
  image_url?: string
  billing_interval?: BillingInterval
  is_active?: boolean
}

/** A prebuilt payment page users can drop into their generated project. */
export interface PaymentTemplate {
  key: string
  name: string
  tagline: string
  description: string
  /** Font Awesome icon name, e.g. 'fa-cart-shopping'. */
  icon: string
  /** Route the page gets in the user's app, e.g. '/store'. */
  route: string
  /** Where the files land inside the project. */
  app_dir: string
  features: string[]
  installed: boolean
}

export interface TemplateInstallResult {
  installed: boolean
  key: string
  name: string
  route: string
  app_dir: string
  files_created: string[]
  templates: PaymentTemplate[]
}

export type OrderStatus = 'pending' | 'paid' | 'fulfilled' | 'canceled' | 'refunded'

export interface OrderItem {
  id: number
  product_id: number | null
  product_name: string
  unit_price_cents: number
  quantity: number
}

export interface Order {
  id: number
  status: OrderStatus
  amount_total_cents: number
  currency: string
  customer_id: number | null
  customer_email: string
  customer_name: string
  stripe_checkout_session_id: string
  stripe_payment_intent_id: string
  paid_at: string | null
  fulfilled_at: string | null
  created_at: string
  updated_at: string
  items: OrderItem[]
}

export interface Customer {
  id: number
  name: string
  email: string
  display_name: string
  phone: string
  notes: string
  source: 'manual' | 'checkout'
  orders_count: number
  total_spent_cents: number
  created_at: string
  updated_at: string
}

export interface CustomerPayload {
  name?: string
  email?: string
  phone?: string
  notes?: string
}

export interface PaymentLinkResult {
  checkout_url: string
  order: Order
}

export interface OverviewStats {
  configured: boolean
  currency: string
  products_total: number
  products_active: number
  customers_total: number
  orders_total: number
  orders_pending: number
  orders_paid_30d: number
  revenue_cents_30d: number
}

export interface OverviewPayload {
  stats: OverviewStats
  recent_orders: Order[]
}

export interface CheckoutSessionStatus {
  status: OrderStatus
  amount_total_cents: number
  currency: string
}
