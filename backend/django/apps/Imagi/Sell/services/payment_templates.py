"""
Prebuilt payment pages the Sell workspace drops into a user's generated
project.

Each template is a self-contained Vue app written into the project's
frontend (frontend/vuejs/src/apps/<app>/); the generated root router
auto-discovers each app's router module, so installing the files is all it
takes to add the page. The pages talk to Imagi's public storefront API and
hand the customer to Stripe's hosted checkout, which is the point: the
generated app never holds Stripe keys, never sees card details, and prices
always come from the project's Sell catalog. Users get a secure payment
flow they can drop in instead of vibe-coding their own Stripe integration.
"""

import os

from django.conf import settings as django_settings

from apps.Imagi.Build.models import ProjectFile
from apps.Imagi.Build.services.create_file_service import CreateFileService
from apps.Imagi.Build.services.project_files_service import ensure_working_copy

from .sell_service import SellServiceError


def storefront_api_base() -> str:
    base = getattr(django_settings, 'SELL_STOREFRONT_API_BASE', '') or 'http://localhost:8000'
    return base.rstrip('/')


# ---------------------------------------------------------------------------
# Generated code shared by every template
# ---------------------------------------------------------------------------


def _storefront_service_ts(project) -> str:
    """The API client baked into the generated app, keyed to this project."""
    return f"""/**
 * Imagi Sell storefront client — a prebuilt, secure payment flow.
 *
 * Payments run on Imagi's servers and Stripe's hosted checkout page. This
 * app never holds Stripe API keys and never sees card details: prices come
 * from your Sell catalog, and this client only starts a checkout and reads
 * its status afterwards.
 *
 * Manage products, orders, and customers from this project's Sell
 * workspace in Imagi.
 */

export const IMAGI_PROJECT_ID = {project.id}
export const IMAGI_API_BASE = '{storefront_api_base()}'

const storefront = `${{IMAGI_API_BASE}}/api/v1/sell/storefront/${{IMAGI_PROJECT_ID}}`

export type BillingInterval = 'one_time' | 'month' | 'year'

export interface StoreProduct {{
  id: number
  name: string
  description: string
  price_cents: number
  image_url: string
  billing_interval: BillingInterval
}}

export interface Catalog {{
  currency: string
  products: StoreProduct[]
}}

export interface CheckoutStatus {{
  status: 'pending' | 'paid' | 'fulfilled' | 'canceled' | 'refunded'
  amount_total_cents: number
  currency: string
}}

async function request<T>(path: string, init?: RequestInit): Promise<T> {{
  const response = await fetch(`${{storefront}}${{path}}`, {{
    headers: {{ 'Content-Type': 'application/json' }},
    ...init,
  }})
  const data = await response.json().catch(() => ({{}}))
  if (!response.ok) {{
    throw new Error((data as {{ error?: string }}).error || 'The store is unavailable right now.')
  }}
  return data as T
}}

export function fetchCatalog(): Promise<Catalog> {{
  return request<Catalog>('/products/')
}}

/**
 * Start a Stripe Checkout for the given items and send the customer to
 * Stripe's hosted payment page. `returnPath` is where Stripe brings them
 * back ('/store' -> /store/success or /store/cancel).
 */
export async function startCheckout(
  items: Array<{{ product_id: number; quantity?: number }}>,
  returnPath: string,
): Promise<void> {{
  const origin = window.location.origin
  const {{ checkout_url }} = await request<{{ checkout_url: string }}>('/checkout/', {{
    method: 'POST',
    body: JSON.stringify({{
      items,
      // Stripe substitutes the real session id into the placeholder.
      success_url: `${{origin}}${{returnPath}}/success?session_id={{CHECKOUT_SESSION_ID}}`,
      cancel_url: `${{origin}}${{returnPath}}/cancel`,
    }}),
  }})
  window.location.assign(checkout_url)
}}

export function fetchCheckoutStatus(sessionId: string): Promise<CheckoutStatus> {{
  return request<CheckoutStatus>(`/sessions/${{encodeURIComponent(sessionId)}}/`)
}}

export function formatMoney(cents: number, currency: string): string {{
  try {{
    return new Intl.NumberFormat(undefined, {{
      style: 'currency',
      currency: currency.toUpperCase(),
    }}).format(cents / 100)
  }} catch {{
    return `$${{(cents / 100).toFixed(2)}}`
  }}
}}
"""


def _checkout_return_view(back_path: str, back_label: str) -> str:
    """Success/cancel landing page; polls the order until Stripe confirms."""
    return f"""<template>
  <div class="min-h-screen bg-white dark:bg-[#0a0a0a] flex items-center justify-center px-4 transition-colors duration-500">
    <div class="max-w-md w-full text-center py-24">
      <template v-if="canceled">
        <div class="w-16 h-16 mx-auto mb-6 rounded-full bg-gray-100 dark:bg-white/[0.06] flex items-center justify-center">
          <i class="fas fa-arrow-rotate-left text-xl text-gray-500 dark:text-gray-400"></i>
        </div>
        <h1 class="text-2xl font-semibold text-gray-900 dark:text-white mb-3">Checkout canceled</h1>
        <p class="text-gray-500 dark:text-gray-400 mb-8">No charge was made. You can pick up right where you left off.</p>
      </template>

      <template v-else-if="state === 'checking'">
        <div class="w-16 h-16 mx-auto mb-6 rounded-full bg-gray-100 dark:bg-white/[0.06] flex items-center justify-center">
          <div class="w-6 h-6 border-2 border-gray-300 dark:border-white/20 border-t-gray-900 dark:border-t-white rounded-full animate-spin"></div>
        </div>
        <h1 class="text-2xl font-semibold text-gray-900 dark:text-white mb-3">Confirming your payment…</h1>
        <p class="text-gray-500 dark:text-gray-400 mb-8">This usually takes a moment.</p>
      </template>

      <template v-else-if="state === 'paid'">
        <div class="w-16 h-16 mx-auto mb-6 rounded-full bg-emerald-100 dark:bg-emerald-900/20 flex items-center justify-center">
          <i class="fas fa-check text-xl text-emerald-600 dark:text-emerald-400"></i>
        </div>
        <h1 class="text-2xl font-semibold text-gray-900 dark:text-white mb-3">Thank you!</h1>
        <p class="text-gray-500 dark:text-gray-400 mb-8">
          Your payment{{{{ amount ? ` of ${{amount}}` : '' }}}} was received. A receipt is on its way to your email.
        </p>
      </template>

      <template v-else>
        <div class="w-16 h-16 mx-auto mb-6 rounded-full bg-amber-100 dark:bg-amber-900/20 flex items-center justify-center">
          <i class="fas fa-hourglass-half text-xl text-amber-600 dark:text-amber-400"></i>
        </div>
        <h1 class="text-2xl font-semibold text-gray-900 dark:text-white mb-3">Payment still processing</h1>
        <p class="text-gray-500 dark:text-gray-400 mb-8">
          We haven't received confirmation yet. If you completed the payment, it will show up shortly — check your email for a receipt.
        </p>
      </template>

      <router-link
        to="{back_path}"
        class="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-full font-medium transition-transform duration-300 hover:scale-[1.02]"
      >
        <i class="fas fa-arrow-left text-sm"></i>
        {back_label}
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import {{ onBeforeUnmount, onMounted, ref }} from 'vue'
import {{ useRoute }} from 'vue-router'
import {{ fetchCheckoutStatus, formatMoney }} from '../services/storefront'

withDefaults(defineProps<{{ canceled?: boolean }}>(), {{ canceled: false }})

const route = useRoute()
const state = ref<'checking' | 'paid' | 'pending'>('checking')
const amount = ref('')

let attempts = 0
let timer: ReturnType<typeof setTimeout> | null = null

async function poll() {{
  const sessionId = String(route.query.session_id || '')
  if (!sessionId) {{
    state.value = 'pending'
    return
  }}
  try {{
    const status = await fetchCheckoutStatus(sessionId)
    if (status.status === 'paid' || status.status === 'fulfilled') {{
      amount.value = formatMoney(status.amount_total_cents, status.currency)
      state.value = 'paid'
      return
    }}
  }} catch {{
    // Keep polling; the backend may still be syncing with Stripe.
  }}
  attempts += 1
  if (attempts < 8) {{
    timer = setTimeout(poll, 1500)
  }} else {{
    state.value = 'pending'
  }}
}}

onMounted(poll)
onBeforeUnmount(() => {{
  if (timer) clearTimeout(timer)
}})
</script>
"""


# ---------------------------------------------------------------------------
# Template: one-time checkout storefront (/store)
# ---------------------------------------------------------------------------


def _store_view() -> str:
    return """<template>
  <div class="min-h-screen bg-white dark:bg-[#0a0a0a] transition-colors duration-500">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16">
      <div class="mb-14 text-center">
        <h1 class="text-4xl sm:text-5xl font-semibold text-gray-900 dark:text-white mb-4 tracking-tight">Store</h1>
        <p class="text-lg text-gray-500 dark:text-gray-400 max-w-2xl mx-auto">
          Secure checkout powered by Stripe — you'll be taken to Stripe's payment page to finish your purchase.
        </p>
      </div>

      <div v-if="loading" class="flex justify-center py-20">
        <div class="w-8 h-8 border-2 border-gray-200 dark:border-white/10 border-t-gray-900 dark:border-t-white rounded-full animate-spin"></div>
      </div>

      <div v-else-if="error" class="max-w-md mx-auto rounded-2xl bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800/30 p-6 text-center">
        <p class="text-red-700 dark:text-red-300">{{ error }}</p>
      </div>

      <div v-else-if="!products.length" class="text-center py-20">
        <p class="text-gray-500 dark:text-gray-400">Nothing for sale just yet — check back soon.</p>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="product in products"
          :key="product.id"
          class="rounded-2xl bg-white/50 dark:bg-white/[0.03] border border-gray-200 dark:border-white/[0.08] overflow-hidden transition-all duration-300 hover:border-gray-300 dark:hover:border-white/[0.15] hover:shadow-lg flex flex-col"
        >
          <img
            v-if="product.image_url"
            :src="product.image_url"
            :alt="product.name"
            class="w-full h-44 object-cover"
          />
          <div class="p-6 flex flex-col flex-1">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">{{ product.name }}</h2>
            <p v-if="product.description" class="text-sm text-gray-500 dark:text-gray-400 mb-4 flex-1">{{ product.description }}</p>
            <div class="flex items-center justify-between gap-3 mt-auto pt-2">
              <span class="text-xl font-semibold text-gray-900 dark:text-white tabular-nums">
                {{ formatMoney(product.price_cents, currency) }}
              </span>
              <button
                type="button"
                :disabled="buyingId !== null"
                class="inline-flex items-center gap-2 px-5 py-2.5 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-full text-sm font-medium transition-transform duration-300 hover:scale-[1.03] disabled:opacity-50 disabled:hover:scale-100"
                @click="buy(product)"
              >
                <i v-if="buyingId === product.id" class="fas fa-circle-notch animate-spin"></i>
                <i v-else class="fas fa-lock text-xs"></i>
                Buy now
              </button>
            </div>
          </div>
        </div>
      </div>

      <p class="mt-12 text-center text-sm text-gray-400 dark:text-gray-500">
        <i class="fas fa-lock mr-1.5"></i>
        Payments are handled by Stripe. Card details never touch this site.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  fetchCatalog,
  formatMoney,
  startCheckout,
  type StoreProduct,
} from '../services/storefront'

const loading = ref(true)
const error = ref('')
const currency = ref('usd')
const products = ref<StoreProduct[]>([])
const buyingId = ref<number | null>(null)

onMounted(async () => {
  try {
    const catalog = await fetchCatalog()
    currency.value = catalog.currency
    // Subscriptions are sold on the pricing page; the store sells one-time items.
    products.value = catalog.products.filter(p => p.billing_interval === 'one_time')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load the store.'
  } finally {
    loading.value = false
  }
})

async function buy(product: StoreProduct) {
  buyingId.value = product.id
  try {
    await startCheckout([{ product_id: product.id, quantity: 1 }], '/store')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not start the checkout.'
    buyingId.value = null
  }
}
</script>
"""


def _store_router() -> str:
    return """import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/store',
    name: 'store',
    component: () => import('../views/StoreView.vue'),
    meta: { title: 'Store' }
  },
  {
    path: '/store/success',
    name: 'store-checkout-success',
    component: () => import('../views/CheckoutReturnView.vue'),
    meta: { title: 'Payment' }
  },
  {
    path: '/store/cancel',
    name: 'store-checkout-cancel',
    component: () => import('../views/CheckoutReturnView.vue'),
    props: { canceled: true },
    meta: { title: 'Checkout canceled' }
  }
]

export { routes }
export default routes
"""


def checkout_template_files(project) -> list:
    app = 'frontend/vuejs/src/apps/store'
    return [
        {'name': f'{app}/services/storefront.ts', 'type': 'typescript',
         'content': _storefront_service_ts(project)},
        {'name': f'{app}/views/StoreView.vue', 'type': 'vue', 'content': _store_view()},
        {'name': f'{app}/views/CheckoutReturnView.vue', 'type': 'vue',
         'content': _checkout_return_view('/store', 'Back to the store')},
        {'name': f'{app}/router/index.ts', 'type': 'typescript', 'content': _store_router()},
        {'name': f'{app}/index.ts', 'type': 'typescript',
         'content': "export { default as routes } from './router'\n"},
    ]


# ---------------------------------------------------------------------------
# Template: subscription plans page (/pricing)
# ---------------------------------------------------------------------------


def _pricing_view() -> str:
    return """<template>
  <div class="min-h-screen bg-white dark:bg-[#0a0a0a] transition-colors duration-500">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-16">
      <div class="mb-14 text-center">
        <h1 class="text-4xl sm:text-5xl font-semibold text-gray-900 dark:text-white mb-4 tracking-tight">Plans &amp; pricing</h1>
        <p class="text-lg text-gray-500 dark:text-gray-400 max-w-2xl mx-auto">
          Pick a plan and subscribe through Stripe's secure checkout. Cancel anytime from your receipt email.
        </p>
      </div>

      <div v-if="loading" class="flex justify-center py-20">
        <div class="w-8 h-8 border-2 border-gray-200 dark:border-white/10 border-t-gray-900 dark:border-t-white rounded-full animate-spin"></div>
      </div>

      <div v-else-if="error" class="max-w-md mx-auto rounded-2xl bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800/30 p-6 text-center">
        <p class="text-red-700 dark:text-red-300">{{ error }}</p>
      </div>

      <div v-else-if="!plans.length" class="text-center py-20">
        <p class="text-gray-500 dark:text-gray-400">No plans are available yet — check back soon.</p>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 justify-center">
        <div
          v-for="plan in plans"
          :key="plan.id"
          class="rounded-2xl bg-white/50 dark:bg-white/[0.03] border border-gray-200 dark:border-white/[0.08] p-8 flex flex-col transition-all duration-300 hover:border-gray-300 dark:hover:border-white/[0.15] hover:shadow-lg"
        >
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">{{ plan.name }}</h2>
          <div class="flex items-baseline gap-1 mb-4">
            <span class="text-3xl font-semibold text-gray-900 dark:text-white tabular-nums">
              {{ formatMoney(plan.price_cents, currency) }}
            </span>
            <span class="text-sm text-gray-500 dark:text-gray-400">/ {{ plan.billing_interval === 'year' ? 'year' : 'month' }}</span>
          </div>
          <p v-if="plan.description" class="text-sm text-gray-500 dark:text-gray-400 mb-6 flex-1 whitespace-pre-line">{{ plan.description }}</p>
          <button
            type="button"
            :disabled="subscribingId !== null"
            class="w-full inline-flex items-center justify-center gap-2 px-5 py-3 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-full text-sm font-medium transition-transform duration-300 hover:scale-[1.02] disabled:opacity-50 disabled:hover:scale-100 mt-auto"
            @click="subscribe(plan)"
          >
            <i v-if="subscribingId === plan.id" class="fas fa-circle-notch animate-spin"></i>
            <i v-else class="fas fa-lock text-xs"></i>
            Subscribe
          </button>
        </div>
      </div>

      <p class="mt-12 text-center text-sm text-gray-400 dark:text-gray-500">
        <i class="fas fa-lock mr-1.5"></i>
        Subscriptions are billed by Stripe. Card details never touch this site.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  fetchCatalog,
  formatMoney,
  startCheckout,
  type StoreProduct,
} from '../services/storefront'

const loading = ref(true)
const error = ref('')
const currency = ref('usd')
const plans = ref<StoreProduct[]>([])
const subscribingId = ref<number | null>(null)

onMounted(async () => {
  try {
    const catalog = await fetchCatalog()
    currency.value = catalog.currency
    // Only subscription products belong here; one-time items live in the store.
    plans.value = catalog.products.filter(p => p.billing_interval !== 'one_time')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load the plans.'
  } finally {
    loading.value = false
  }
})

async function subscribe(plan: StoreProduct) {
  subscribingId.value = plan.id
  try {
    await startCheckout([{ product_id: plan.id, quantity: 1 }], '/pricing')
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not start the checkout.'
    subscribingId.value = null
  }
}
</script>
"""


def _pricing_router() -> str:
    return """import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/pricing',
    name: 'pricing',
    component: () => import('../views/PricingView.vue'),
    meta: { title: 'Pricing' }
  },
  {
    path: '/pricing/success',
    name: 'pricing-checkout-success',
    component: () => import('../views/CheckoutReturnView.vue'),
    meta: { title: 'Subscription' }
  },
  {
    path: '/pricing/cancel',
    name: 'pricing-checkout-cancel',
    component: () => import('../views/CheckoutReturnView.vue'),
    props: { canceled: true },
    meta: { title: 'Checkout canceled' }
  }
]

export { routes }
export default routes
"""


def subscription_template_files(project) -> list:
    app = 'frontend/vuejs/src/apps/pricing'
    return [
        {'name': f'{app}/services/storefront.ts', 'type': 'typescript',
         'content': _storefront_service_ts(project)},
        {'name': f'{app}/views/PricingView.vue', 'type': 'vue', 'content': _pricing_view()},
        {'name': f'{app}/views/CheckoutReturnView.vue', 'type': 'vue',
         'content': _checkout_return_view('/pricing', 'Back to plans')},
        {'name': f'{app}/router/index.ts', 'type': 'typescript', 'content': _pricing_router()},
        {'name': f'{app}/index.ts', 'type': 'typescript',
         'content': "export { default as routes } from './router'\n"},
    ]


# ---------------------------------------------------------------------------
# Registry + install
# ---------------------------------------------------------------------------

TEMPLATES = {
    'checkout': {
        'key': 'checkout',
        'name': 'One-time checkout',
        'tagline': 'A ready-made store page for single purchases',
        'description': (
            'Adds a Store page to your app that lists your one-time products '
            'and sends customers to Stripe\'s secure checkout. Paid orders '
            'show up in the Orders tab automatically.'
        ),
        'icon': 'fa-cart-shopping',
        'route': '/store',
        'app_dir': 'frontend/vuejs/src/apps/store',
        'features': [
            'Store page listing your one-time products',
            'Stripe-hosted checkout — card details never touch your app',
            'Thank-you page that confirms the payment',
            'Orders and customers tracked in this workspace',
        ],
        'generate': checkout_template_files,
    },
    'subscriptions': {
        'key': 'subscriptions',
        'name': 'Subscription plans',
        'tagline': 'A pricing page for recurring memberships',
        'description': (
            'Adds a Pricing page that shows your monthly and yearly plans '
            'and lets customers subscribe through Stripe\'s secure checkout. '
            'Create subscription products in the Products tab first.'
        ),
        'icon': 'fa-arrows-rotate',
        'route': '/pricing',
        'app_dir': 'frontend/vuejs/src/apps/pricing',
        'features': [
            'Pricing page with your monthly and yearly plans',
            'Recurring billing handled entirely by Stripe',
            'Thank-you page that confirms the subscription',
            'New subscribers appear in Customers automatically',
        ],
        'generate': subscription_template_files,
    },
}


def _is_installed(project, spec) -> bool:
    """A template counts as installed when its app exists in the project."""
    marker = spec['app_dir'] + '/'
    if ProjectFile.objects.filter(project=project, path__startswith=marker).exists():
        return True
    project_path = project.project_path or ''
    return bool(project_path) and os.path.isdir(os.path.join(project_path, spec['app_dir']))


def list_templates(project) -> list:
    """Template metadata for the gallery, with per-project installed state."""
    return [
        {
            'key': spec['key'],
            'name': spec['name'],
            'tagline': spec['tagline'],
            'description': spec['description'],
            'icon': spec['icon'],
            'route': spec['route'],
            'app_dir': spec['app_dir'],
            'features': spec['features'],
            'installed': _is_installed(project, spec),
        }
        for spec in TEMPLATES.values()
    ]


def install_template(project, key: str) -> dict:
    """
    Write a template's files into the project (disk + database copy).
    Reinstalling overwrites the template's own files and nothing else.
    """
    spec = TEMPLATES.get(key)
    if not spec:
        raise SellServiceError('Unknown payment template.')

    # Make sure the working copy exists before writing into it (production
    # cold starts serve projects from the database).
    ensure_working_copy(project)

    file_service = CreateFileService(project=project)
    created = []
    for file_data in spec['generate'](project):
        result = file_service.create_file(file_data)
        created.append(result['path'])

    return {
        'key': spec['key'],
        'name': spec['name'],
        'route': spec['route'],
        'app_dir': spec['app_dir'],
        'files_created': created,
    }
