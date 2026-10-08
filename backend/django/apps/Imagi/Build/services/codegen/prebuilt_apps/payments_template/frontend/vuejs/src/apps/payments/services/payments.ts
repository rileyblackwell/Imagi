/**
 * Payments client: the one way this app talks to its payment backend.
 *
 * Payments run on Imagi's servers and Stripe's hosted checkout page. This app
 * never holds Stripe keys and never sees card details. Prices always come
 * from the business's price list in Imagi, so a changed request can't change
 * what a customer is charged. Maintained by Imagi.
 */
import { paymentsConfig } from '../config'

const base = () =>
  `${paymentsConfig.apiBase.replace(/\/$/, '')}/api/v1/sell/storefront/${paymentsConfig.projectId}`

export type BillingInterval = 'one_time' | 'month' | 'year' | 'usage'

export interface Price {
  id: number
  name: string
  description: string
  price_cents: number
  image_url: string
  billing_interval: BillingInterval
  /** Pay as you go: what one unit is, and how many units price_cents buys. */
  usage_unit_label: string
  usage_unit_count: number
}

export interface Catalog {
  currency: string
  products: Price[]
}

export interface CheckoutStatus {
  status: 'pending' | 'paid' | 'fulfilled' | 'canceled' | 'refunded'
  amount_total_cents: number
  currency: string
  mode: 'payment' | 'subscription'
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${base()}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error((data as { error?: string }).error || 'Payments are unavailable right now.')
  }
  return data as T
}

export function fetchCatalog(): Promise<Catalog> {
  return request<Catalog>('/products/')
}

export const isPlan = (price: Price) => price.billing_interval !== 'one_time'

/**
 * Start a Stripe Checkout and send the customer to Stripe's payment page.
 * `returnPath` is where Stripe brings them back ('/pricing' ends at
 * /pricing/success or /pricing/cancel). Pass the signed-in customer's email
 * for plans, so the subscription belongs to their account.
 */
export async function startCheckout(
  items: Array<{ product_id: number; quantity?: number }>,
  returnPath: string,
  customerEmail = ''
): Promise<void> {
  const origin = window.location.origin
  const { checkout_url } = await request<{ checkout_url: string }>('/checkout/', {
    method: 'POST',
    body: JSON.stringify({
      items,
      customer_email: customerEmail,
      // Stripe puts the real session id in place of the placeholder.
      success_url: `${origin}${returnPath}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}${returnPath}/cancel`
    })
  })
  window.location.assign(checkout_url)
}

export function fetchCheckoutStatus(sessionId: string): Promise<CheckoutStatus> {
  return request<CheckoutStatus>(`/sessions/${encodeURIComponent(sessionId)}/`)
}

export function formatMoney(cents: number, currency: string, exact = false): string {
  try {
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: currency.toUpperCase(),
      maximumFractionDigits: exact ? 4 : 2
    }).format(cents / 100)
  } catch {
    return `$${(cents / 100).toFixed(2)}`
  }
}

/** "$12 / month", "$1 per 1,000 messages", "$30". */
export function describePrice(price: Price, currency: string): { amount: string; per: string } {
  const amount = formatMoney(price.price_cents, currency)
  if (price.billing_interval === 'usage') {
    const unit = price.usage_unit_label || 'unit'
    const count = price.usage_unit_count > 1 ? `${price.usage_unit_count.toLocaleString()} ` : ''
    return { amount, per: `per ${count}${unit}${price.usage_unit_count > 1 ? 's' : ''}, billed monthly` }
  }
  if (price.billing_interval === 'month') return { amount, per: '/ month' }
  if (price.billing_interval === 'year') return { amount, per: '/ year' }
  return { amount, per: '' }
}
