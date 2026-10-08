<!--
  SellOverview.vue - The Sell console: the guided setup for taking payments,
  then the numbers once money is coming in.

  Four steps on a rail, each with its state on its node (ok done, wait needs
  you, plain to do): connect Stripe (Stripe Connect's hosted sign-up), choose
  how the business charges, set the prices, and add Imagi's prebuilt payment
  pages to the app. Only the next step's action wears the lit button.

  Stripe sends the founder back here from its sign-up with ?stripe=return (or
  ?stripe=refresh when the link expired), which this view picks up.
-->
<template>
  <div>
    <LoadingSpinner v-if="loading" />

    <template v-else>
      <div v-if="loadError" class="mb-6" :class="ui.errorBox">{{ loadError }}</div>

      <!-- Numbers, once payments can come in -->
      <section v-if="overview && store.isConfigured" class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <div v-for="stat in statCards" :key="stat.label" class="p-5" :class="ui.card">
          <p class="text-xs font-semibold uppercase tracking-[0.14em] text-ink/50 dark:text-bone/50 mb-2">{{ stat.label }}</p>
          <p class="text-2xl font-semibold text-ink dark:text-white tabular-nums">{{ stat.value }}</p>
          <p :class="ui.hintText" class="mt-1">{{ stat.caption }}</p>
        </div>
      </section>

      <div class="flex flex-wrap items-end justify-between gap-3 mb-5">
        <div>
          <h2 :class="ui.headingText">{{ allDone ? 'Payments are set up' : 'Set up payments' }}</h2>
          <p :class="ui.bodyText" class="mt-1">
            {{ allDone
              ? 'Customers can pay in your app. Change anything below at any time.'
              : `${doneCount} of 4 done. Each step takes a minute or two.` }}
          </p>
        </div>
        <span
          v-if="settings?.connection_type && settings.is_test_mode"
          class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-[11px] font-semibold uppercase tracking-[0.1em] whitespace-nowrap"
          :class="statusTones.pending"
          title="Stripe test mode: checkouts use test cards and no real money moves."
        >
          <span class="w-1.5 h-1.5 rounded-full bg-current"></span>
          Test mode
        </span>
      </div>

      <ol class="console-rail">
        <!-- 1. Connect Stripe -->
        <li class="console-step">
          <StepNode :index="1" :state="connectState" />
          <div class="p-6" :class="ui.card">
            <div class="flex flex-wrap items-start justify-between gap-4">
              <div class="min-w-0 max-w-xl">
                <h3 :class="ui.panelHeading">Connect Stripe</h3>
                <p :class="ui.bodyText" class="mt-1">
                  <template v-if="connectState === 'done'">
                    Connected to {{ accountLabel }}. Payments go straight to this Stripe account.
                  </template>
                  <template v-else-if="connectState === 'wait'">
                    Your Stripe account is linked, but Stripe still needs a few details before it can take payments.
                  </template>
                  <template v-else>
                    Stripe handles the cards and pays out to your bank. Create a Stripe account or sign in to the one you have; it takes a few minutes.
                  </template>
                </p>
                <div v-if="settings?.connection_type === 'connect'" class="flex flex-wrap gap-2 mt-3">
                  <span class="console-chip" :class="settings.connect_charges_enabled ? statusTones.success : statusTones.neutral">
                    {{ settings.connect_charges_enabled ? 'Payments on' : 'Payments off' }}
                  </span>
                  <span class="console-chip" :class="settings.connect_payouts_enabled ? statusTones.success : statusTones.neutral">
                    {{ settings.connect_payouts_enabled ? 'Payouts on' : 'Payouts off' }}
                  </span>
                </div>
              </div>
              <div class="flex flex-wrap items-center gap-3">
                <button
                  v-if="connectState !== 'done'"
                  type="button"
                  :class="nextStep === 1 ? ui.primaryBtn : ui.secondaryBtn"
                  :disabled="connecting"
                  @click="connect"
                >
                  <i v-if="connecting" class="fas fa-circle-notch animate-spin text-xs"></i>
                  {{ connectState === 'wait' ? 'Finish Stripe setup' : 'Connect with Stripe' }}
                </button>
                <button
                  v-if="connectState === 'wait'"
                  type="button"
                  :class="ui.secondaryBtn"
                  :disabled="refreshing"
                  @click="refresh"
                >
                  <i v-if="refreshing" class="fas fa-circle-notch animate-spin text-xs"></i>
                  Check again
                </button>
                <a
                  v-if="connectState === 'done'"
                  href="https://dashboard.stripe.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  :class="ui.secondaryBtn"
                >
                  Open Stripe
                  <i class="fas fa-arrow-up-right-from-square text-[10px] opacity-60"></i>
                </a>
              </div>
            </div>
            <div v-if="connectError" class="mt-4" :class="ui.errorBox">{{ connectError }}</div>
            <p v-if="connectState === 'todo'" :class="ui.hintText" class="mt-4">
              Already have API keys you'd rather use?
              <router-link :to="{ name: 'sell-settings', params: { projectName } }" :class="ui.inlineLink">Add them in Settings</router-link>.
            </p>
          </div>
        </li>

        <!-- 2. Choose how you charge -->
        <li class="console-step">
          <StepNode :index="2" :state="chooseState" />
          <div class="p-6" :class="ui.card">
            <h3 :class="ui.panelHeading">Choose how you charge</h3>
            <p :class="ui.bodyText" class="mt-1 mb-5">Pick one or more. You can change this later.</p>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3" role="group" aria-label="Ways to charge">
              <button
                v-for="model in paymentModels"
                :key="model.key"
                type="button"
                class="console-option focus-ring"
                :class="{ 'console-option--on': chosen.includes(model.key) }"
                :aria-pressed="chosen.includes(model.key)"
                :disabled="savingModels"
                @click="toggleModel(model.key)"
              >
                <span class="console-option__check" aria-hidden="true">
                  <i v-if="chosen.includes(model.key)" class="fas fa-check"></i>
                </span>
                <span class="block text-sm font-semibold text-ink dark:text-bone">{{ model.title }}</span>
                <span class="block text-sm text-ink/60 dark:text-bone/60 mt-1">{{ model.body }}</span>
                <span class="block text-xs text-ink/50 dark:text-bone/50 mt-3">Good for {{ model.examples }}</span>
              </button>
            </div>
            <div v-if="modelsError" class="mt-4" :class="ui.errorBox">{{ modelsError }}</div>
          </div>
        </li>

        <!-- 3. Set your prices -->
        <li class="console-step">
          <StepNode :index="3" :state="pricesState" />
          <div class="p-6" :class="ui.card">
            <div class="flex flex-wrap items-start justify-between gap-4">
              <div class="max-w-xl">
                <h3 :class="ui.panelHeading">Set your prices</h3>
                <p :class="ui.bodyText" class="mt-1">
                  {{ chosen.length ? 'Add at least one price for each way you charge.' : 'Choose how you charge first.' }}
                </p>
              </div>
              <router-link :to="{ name: 'sell-products', params: { projectName } }" :class="ui.textLink">
                All prices
              </router-link>
            </div>
            <div v-if="chosenModels.length" class="mt-5 divide-y divide-[color:var(--sl-line)] border-y border-[color:var(--sl-line)]">
              <div v-for="model in chosenModels" :key="model.key" class="flex flex-wrap items-center gap-3 py-3.5">
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-ink dark:text-bone">{{ model.title }}</p>
                  <p :class="ui.hintText" class="mt-0.5 truncate">
                    {{ pricesFor(model.key).length
                      ? pricesFor(model.key).map(p => `${p.name} · ${describePrice(p, store.currency)}`).join('  ·  ')
                      : 'No prices yet' }}
                  </p>
                </div>
                <router-link
                  :to="{ name: 'sell-products', params: { projectName }, query: { new: '1', interval: model.key === 'subscription' ? 'month' : model.key } }"
                  :class="nextStep === 3 && !pricesFor(model.key).length ? ui.primaryBtn : ui.secondaryBtn"
                >
                  <i class="fas fa-plus text-xs"></i>
                  Add price
                </router-link>
              </div>
            </div>
          </div>
        </li>

        <!-- 4. Add payments to your app -->
        <li class="console-step">
          <StepNode :index="4" :state="appState" />
          <div class="p-6" :class="ui.card">
            <div class="flex flex-wrap items-start justify-between gap-4">
              <div class="max-w-xl">
                <h3 :class="ui.panelHeading">Add payments to your app</h3>
                <p :class="ui.bodyText" class="mt-1">
                  Imagi adds ready-made payment pages to your app. They're built and kept secure by Imagi,
                  then restyled to match your site. Customers pay on Stripe's checkout page, so card details never touch your app.
                </p>
              </div>
              <button
                type="button"
                :class="nextStep === 4 ? ui.primaryBtn : ui.secondaryBtn"
                :disabled="installing || !chosen.length"
                @click="install"
              >
                <i v-if="installing" class="fas fa-circle-notch animate-spin text-xs"></i>
                {{ appButtonLabel }}
              </button>
            </div>

            <div v-if="wantedPages.length" class="mt-5 grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div
                v-for="page in wantedPages"
                :key="page.key"
                class="flex items-start gap-3 p-4 rounded-xl border border-[color:var(--sl-line)]"
              >
                <code class="font-mono text-xs px-2 py-1 rounded-md bg-[color:var(--sl-chip-bg)] text-ink dark:text-bone">{{ page.route }}</code>
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-ink dark:text-bone">{{ page.name }}</p>
                  <p :class="ui.hintText" class="mt-0.5">{{ page.description }}</p>
                </div>
                <span v-if="page.installed" class="console-chip" :class="statusTones.success">In app</span>
              </div>
            </div>

            <div v-if="installError" class="mt-4" :class="ui.errorBox">{{ installError }}</div>
            <div v-if="installNotice" class="mt-4" :class="ui.successBox">
              {{ installNotice }}
              <router-link :to="{ name: 'builder-workspace', params: { projectName } }" :class="ui.inlineLink">Open Build</router-link>
              to see them.
            </div>

            <details v-if="chosen.includes('usage')" class="console-details mt-5">
              <summary class="text-sm font-medium text-ink dark:text-bone cursor-pointer">How pay as you go is counted</summary>
              <p :class="ui.bodyText" class="mt-3">
                Your app tells Imagi each time a customer uses something you charge for, and Stripe adds it up and bills them monthly.
                Ask Imagi's agent in Build, for example "charge for each message sent", and it wires this in with one line:
              </p>
              <pre class="mt-3 p-3.5 rounded-xl bg-[color:var(--sl-chip-bg)] border border-[color:var(--sl-line)] font-mono text-xs text-ink/80 dark:text-bone/80 overflow-x-auto">from apps.payments import report_usage

report_usage(request.user.email, quantity=1)</pre>
              <p :class="ui.hintText" class="mt-2">
                That call runs on your app's server with a private key Imagi supplies, so it can't be faked from a browser.
              </p>
            </details>
          </div>
        </li>
      </ol>

      <!-- Recent orders -->
      <section v-if="overview?.recent_orders.length" class="mt-10 p-6" :class="ui.card">
        <div class="flex items-center justify-between mb-4">
          <h2 :class="ui.panelHeading">Recent orders</h2>
          <router-link :to="{ name: 'sell-orders', params: { projectName } }" :class="ui.textLink">
            View all
          </router-link>
        </div>
        <div class="space-y-3">
          <div
            v-for="order in overview.recent_orders"
            :key="order.id"
            class="flex items-center gap-3 p-3 rounded-xl border border-ink/10 dark:border-white/[0.08]"
          >
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-ink dark:text-white truncate">{{ orderSummary(order) }}</p>
              <p :class="ui.hintText">
                {{ order.customer_email || 'No email yet' }} · {{ formatDateTime(order.created_at) }}
              </p>
            </div>
            <span class="text-sm font-semibold text-ink dark:text-white tabular-nums">
              {{ formatMoney(order.amount_total_cents, order.currency) }}
            </span>
            <OrderStatusBadge :status="order.status" />
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { LoadingSpinner } from '@/shared/components'
import { statusTones } from '@/shared/styles'
import OrderStatusBadge from '../components/OrderStatusBadge.vue'
import StepNode from '../components/StepNode.vue'
import { extractError } from '../services/sellService'
import { useSellStore } from '../stores/sell'
import type { Order, PaymentModel, Product } from '../types'
import { describePrice, formatDateTime, formatMoney, paymentModels, ui } from '../utils/ui'

type StepState = 'done' | 'wait' | 'todo'

const route = useRoute()
const router = useRouter()
const store = useSellStore()

const projectName = computed(() => String(route.params.projectName))
const settings = computed(() => store.settings)
const overview = computed(() => store.overview)

const loading = ref(true)
const loadError = ref('')
const connecting = ref(false)
const refreshing = ref(false)
const connectError = ref('')
const savingModels = ref(false)
const modelsError = ref('')
const installing = ref(false)
const installError = ref('')
const installNotice = ref('')

// -- Step states ----------------------------------------------------------------

const accountLabel = computed(() =>
  settings.value?.account_name || settings.value?.account_email || 'your Stripe account'
)

const connectState = computed<StepState>(() => {
  if (store.isConfigured) return 'done'
  if (store.isConnected) return 'wait'
  return 'todo'
})

const chosen = computed<PaymentModel[]>(() => store.paymentModels)
const chosenModels = computed(() => paymentModels.filter(m => chosen.value.includes(m.key)))
const chooseState = computed<StepState>(() => (chosen.value.length ? 'done' : 'todo'))

function pricesFor(model: PaymentModel): Product[] {
  return store.products.filter(p => p.is_active && p.pricing_model === model)
}

const pricesState = computed<StepState>(() =>
  chosen.value.length && chosen.value.every(m => pricesFor(m).length) ? 'done' : 'todo'
)

const wantedPages = computed(() => (store.appPayments?.pages ?? []).filter(p => p.enabled))

const appState = computed<StepState>(() => {
  const app = store.appPayments
  if (!app?.installed) return 'todo'
  return app.out_of_date ? 'wait' : 'done'
})

const appButtonLabel = computed(() => {
  if (!store.appPayments?.installed) return 'Add to my app'
  return store.appPayments.out_of_date ? 'Update my app' : 'Reinstall'
})

const states = computed(() => [connectState.value, chooseState.value, pricesState.value, appState.value])
const doneCount = computed(() => states.value.filter(s => s === 'done').length)
const allDone = computed(() => doneCount.value === 4)
/** The first unfinished step: its action is the one lit button. */
const nextStep = computed(() => states.value.findIndex(s => s !== 'done') + 1)

// -- Actions ----------------------------------------------------------------------

async function connect() {
  connecting.value = true
  connectError.value = ''
  try {
    const url = await store.startConnect(route.path)
    window.location.assign(url)
  } catch (error) {
    connectError.value = extractError(error, 'Could not open Stripe.')
    connecting.value = false
  }
}

async function refresh() {
  refreshing.value = true
  connectError.value = ''
  try {
    await store.refreshConnect()
  } catch (error) {
    connectError.value = extractError(error, 'Could not check your Stripe account.')
  } finally {
    refreshing.value = false
  }
}

async function toggleModel(model: PaymentModel) {
  const next = chosen.value.includes(model)
    ? chosen.value.filter(m => m !== model)
    : [...chosen.value, model]
  savingModels.value = true
  modelsError.value = ''
  try {
    await store.saveSettings({ payment_models: next })
    await store.fetchAppPayments()
  } catch (error) {
    modelsError.value = extractError(error, 'Could not save your choice.')
  } finally {
    savingModels.value = false
  }
}

async function install() {
  installing.value = true
  installError.value = ''
  installNotice.value = ''
  try {
    const result = await store.installAppPayments()
    const pages = result.routes.join(' and ')
    installNotice.value = result.restyle_started
      ? `Added ${pages} to your app. Imagi is restyling them to match your site and linking them from it.`
      : `Added ${pages} to your app.`
  } catch (error) {
    installError.value = extractError(error, 'Could not add payments to your app.')
  } finally {
    installing.value = false
  }
}

// -- Numbers ------------------------------------------------------------------------

function orderSummary(order: Order): string {
  const first = order.items[0]
  if (!first) return `Order #${order.id}`
  const extra = order.items.length - 1
  return extra > 0 ? `${first.product_name} + ${extra} more` : `${first.quantity} × ${first.product_name}`
}

const statCards = computed(() => {
  const stats = overview.value?.stats
  if (!stats) return []
  return [
    { label: 'Revenue', value: formatMoney(stats.revenue_cents_30d, stats.currency), caption: 'last 30 days' },
    { label: 'Subscribers', value: stats.subscriptions_active.toLocaleString(), caption: 'active plans' },
    { label: 'Monthly recurring', value: formatMoney(stats.mrr_cents, stats.currency), caption: 'from fixed plans' },
    { label: 'Customers', value: stats.customers_total.toLocaleString(), caption: `${stats.orders_paid_30d} paid orders in 30 days` },
  ]
})

// -- Load ---------------------------------------------------------------------------

onMounted(async () => {
  const stripeReturn = String(route.query.stripe || '')
  if (stripeReturn) {
    // Drop the marker so a reload doesn't repeat this.
    router.replace({ query: { ...route.query, stripe: undefined } })
  }
  if (stripeReturn === 'refresh') {
    // Stripe's sign-up link expired or was reused: open a fresh one.
    await connect()
    return
  }
  try {
    if (!store.settings) await store.fetchSettings()
    if (stripeReturn === 'return' && store.settings?.connection_type === 'connect') {
      await store.refreshConnect().catch(() => undefined)
    }
    await Promise.all([store.fetchOverview(), store.fetchProducts(), store.fetchAppPayments()])
  } catch (error) {
    loadError.value = extractError(error, 'Could not load the Sell console.')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.console-rail {
  position: relative;
  display: grid;
  gap: 1rem;
  padding-left: 2.75rem;
}

/* The rail: a hairline behind the step nodes. */
.console-rail::before {
  content: '';
  position: absolute;
  left: 0.875rem;
  top: 1.5rem;
  bottom: 1.5rem;
  width: 1px;
  background: var(--sl-line-strong);
}

.console-step {
  position: relative;
}

.console-chip {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.625rem;
  border-width: 1px;
  border-radius: 9999px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  white-space: nowrap;
}

.console-option {
  position: relative;
  text-align: left;
  padding: 1rem 2.75rem 1rem 1rem;
  border-radius: 0.875rem;
  border: 1px solid var(--sl-line);
  background: var(--sl-chip-bg);
  transition: border-color 200ms cubic-bezier(0.22, 1, 0.36, 1), background-color 200ms cubic-bezier(0.22, 1, 0.36, 1);
}

.console-option:hover {
  border-color: var(--sl-line-strong);
}

.console-option--on {
  border-color: var(--sl-warm-line);
  background: var(--sl-chip-bg-hover);
}

.console-option:disabled {
  cursor: progress;
}

.console-option__check {
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 9999px;
  border: 1px solid var(--sl-line-strong);
  font-size: 10px;
  color: var(--sl-on-accent);
}

.console-option--on .console-option__check {
  border-color: transparent;
  background: var(--sl-grad);
}

.console-details summary::marker {
  color: var(--sl-muted);
}

@media (max-width: 640px) {
  .console-rail {
    padding-left: 2.25rem;
  }
  .console-rail::before {
    left: 0.75rem;
  }
}
</style>
