/**
 * Types for the Sell module — mirrors the Django Sell app API
 * (backend/django/apps/Imagi/Sell).
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
  /** Checkouts run against Stripe's test mode (no real money moves). */
  is_test_mode: boolean
  /** How Stripe is linked: Stripe Connect, pasted API keys, or not at all. */
  connection_type: 'connect' | 'keys' | ''
  connect_account_id: string
  connect_charges_enabled: boolean
  connect_payouts_enabled: boolean
  connect_details_submitted: boolean
  /** The ways to charge chosen in the console. */
  payment_models: PaymentModel[]
  /** Where the business's published app lives (allowed checkout return origin). */
  app_url: string
  server_key_set: boolean
  /** Stripe webhook URL to register in the Stripe dashboard; empty when the backend has no public base URL configured. */
  stripe_webhook_url: string
  /** Imagi's platform webhook for connected accounts (informational). */
  connect_webhook_url: string
}

export type PaymentModel = 'one_time' | 'subscription' | 'usage'

export interface SellSettingsPayload {
  stripe_publishable_key?: string
  /** Write-only; omit or send '' to keep the stored key. */
  stripe_secret_key?: string
  /** Write-only; omit or send '' to keep the stored secret. */
  stripe_webhook_secret?: string
  currency?: string
  payment_models?: PaymentModel[]
  app_url?: string
}

export interface VerifyResult {
  verified: boolean
  account_name: string
  account_email: string
  charges_enabled: boolean
  settings: SellSettings
}

export type BillingInterval = 'one_time' | 'month' | 'year' | 'usage'

export interface Product {
  id: number
  name: string
  description: string
  price_cents: number
  image_url: string
  billing_interval: BillingInterval
  pricing_model: PaymentModel
  /** Pay as you go: what one unit is, and how many units price_cents buys. */
  usage_unit_label: string
  usage_unit_count: number
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
  usage_unit_label?: string
  usage_unit_count?: number
  is_active?: boolean
}

/** One prebuilt payment page Imagi adds to the user's app. */
export interface AppPaymentPage {
  key: 'pricing' | 'store'
  route: string
  name: string
  description: string
  /** The chosen ways to charge call for this page. */
  enabled: boolean
  /** The app has it now. */
  installed: boolean
}

export interface AppPaymentsState {
  installed: boolean
  pages: AppPaymentPage[]
  /** Installed, but the chosen ways to charge have changed since. */
  out_of_date: boolean
  frontend_dir: string
  backend_dir: string
}

export interface AppPaymentsInstallResult extends AppPaymentsState {
  routes: string[]
  restyle_started: boolean
  files_written: string[]
}

export interface Subscription {
  id: number
  product_id: number | null
  product_name: string
  customer_id: number | null
  customer_email: string
  /** Stripe's status: active, trialing, past_due, canceled, unpaid, … */
  status: string
  is_active: boolean
  cancel_at_period_end: boolean
  current_period_end: string | null
  pricing_model: PaymentModel
  stripe_subscription_id: string
  usage_units_30d: number
  created_at: string
  updated_at: string
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
  prices_by_model: Record<PaymentModel, number>
  subscriptions_active: number
  mrr_cents: number
  usage_units_30d: number
}

export interface OverviewPayload {
  stats: OverviewStats
  recent_orders: Order[]
}

export interface CheckoutSessionStatus {
  status: OrderStatus
  amount_total_cents: number
  currency: string
  mode?: 'payment' | 'subscription'
}
