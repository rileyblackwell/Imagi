<!--
  SellSettings.vue - How the project reaches Stripe, and the details behind
  the console: the connected account (Stripe Connect) or, as an advanced
  fallback, the owner's own API keys; currency and the app's address; the
  server key the app's backend uses; webhook and storefront API endpoints.
-->
<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
    <div class="lg:col-span-2 space-y-6">
    <!-- Connected through Stripe Connect -->
    <section v-if="settings?.connection_type === 'connect'" class="p-6" :class="ui.card">
      <div class="flex items-center gap-3 mb-1.5">
        <h2 :class="ui.panelHeading">Stripe account</h2>
        <span
          class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-[11px] font-semibold uppercase tracking-[0.1em]"
          :class="settings.connect_charges_enabled ? statusTones.success : statusTones.pending"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-current"></span>
          {{ settings.connect_charges_enabled ? 'Connected' : 'Setup unfinished' }}
        </span>
      </div>
      <p :class="ui.bodyText" class="mb-5">
        Linked through Stripe Connect{{ settings.account_name || settings.account_email ? ` to ${settings.account_name || settings.account_email}` : '' }}.
        You own this Stripe account: payments and payouts are yours, and you manage them at stripe.com.
      </p>
      <dl class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div>
          <dt :class="ui.label">Account</dt>
          <dd class="font-mono text-xs text-ink/80 dark:text-bone/80 break-all">{{ settings.connect_account_id }}</dd>
        </div>
        <div>
          <dt :class="ui.label">Payments</dt>
          <dd class="text-sm text-ink/80 dark:text-bone/80">{{ settings.connect_charges_enabled ? 'On' : 'Off' }}</dd>
        </div>
        <div>
          <dt :class="ui.label">Payouts</dt>
          <dd class="text-sm text-ink/80 dark:text-bone/80">{{ settings.connect_payouts_enabled ? 'On' : 'Off' }}</dd>
        </div>
      </dl>
      <div class="flex flex-wrap items-center gap-3">
        <button type="button" :class="ui.secondaryBtn" :disabled="verifying" @click="refreshConnect">
          <i v-if="verifying" class="fas fa-circle-notch animate-spin text-xs"></i>
          Check again
        </button>
        <button type="button" :class="ui.dangerBtn" :disabled="disconnecting" @click="disconnect">
          Disconnect
        </button>
      </div>
      <div v-if="verifyError" class="mt-5" :class="ui.errorBox">{{ verifyError }}</div>
    </section>

    <!-- Not connected: point at the console's one-click path -->
    <section v-else-if="!settings?.connection_type && !showKeys" class="p-6" :class="ui.card">
      <h2 :class="ui.panelHeading" class="mb-1.5">Stripe account</h2>
      <p :class="ui.bodyText" class="mb-5">
        Connect Stripe from the console: Stripe walks you through creating an account or signing in, and there are no keys to copy.
      </p>
      <div class="flex flex-wrap items-center gap-3">
        <router-link :to="{ name: 'sell-overview', params: { projectName: route.params.projectName } }" :class="ui.primaryBtn">
          Connect with Stripe
        </router-link>
        <button type="button" :class="ui.textLink" @click="showKeys = true">Use API keys instead</button>
      </div>
    </section>

    <!-- Credentials form (advanced: the owner's own API keys) -->
    <section v-if="settings?.connection_type === 'keys' || showKeys" class="p-6" :class="ui.card">
      <div class="flex items-center gap-3 mb-1.5">
        <h2 :class="ui.panelHeading">Stripe account</h2>
        <span
          v-if="settings?.is_configured"
          class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border border-emerald-200/80 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-500/10 text-[11px] font-semibold uppercase tracking-[0.1em] text-emerald-700 dark:text-emerald-300"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-current"></span>
          Connected
        </span>
      </div>
      <p :class="ui.bodyText" class="mb-6">
        Advanced. Find these under
        <a href="https://dashboard.stripe.com/apikeys" target="_blank" rel="noopener noreferrer" class="rounded-sm font-medium text-ink/80 dark:text-bone/80 hover:text-ink dark:hover:text-white underline underline-offset-2 decoration-ink/30 dark:decoration-bone/30 hover:decoration-ink/60 dark:hover:decoration-bone/70 transition-colors duration-200 focus-ring">Developers → API keys</a>
        in your Stripe dashboard. Payments go directly to your own Stripe account.
      </p>

      <form class="space-y-5" @submit.prevent="save">
        <div>
          <label :class="ui.label" for="stripe-pk">Publishable key</label>
          <input
            id="stripe-pk"
            v-model="form.stripe_publishable_key"
            type="text"
            placeholder="pk_test_..."
            autocomplete="off"
            spellcheck="false"
            class="font-mono text-xs"
            :class="ui.input"
          />
        </div>
        <div>
          <label :class="ui.label" for="stripe-sk">Secret key</label>
          <input
            id="stripe-sk"
            v-model="form.stripe_secret_key"
            type="password"
            autocomplete="new-password"
            :placeholder="settings?.stripe_secret_key_set ? '•••••••• saved — enter a new key to replace it' : 'sk_test_...'"
            class="font-mono text-xs"
            :class="ui.input"
          />
          <p :class="ui.hintText" class="mt-1.5">
            Stored encrypted and never shown again. Leave blank to keep the saved key.
          </p>
        </div>
        <div>
          <div>
            <label :class="ui.label" for="stripe-whsec">Webhook signing secret <span class="normal-case tracking-normal font-normal">(optional)</span></label>
            <input
              id="stripe-whsec"
              v-model="form.stripe_webhook_secret"
              type="password"
              autocomplete="new-password"
              :placeholder="settings?.stripe_webhook_secret_set ? '•••••••• saved — enter a new secret to replace it' : 'whsec_...'"
              class="font-mono text-xs"
              :class="ui.input"
            />
            <p :class="ui.hintText" class="mt-1.5">Lets Stripe push payment updates to Imagi.</p>
          </div>
        </div>

        <div v-if="saveError" :class="ui.errorBox">{{ saveError }}</div>
        <div v-if="saveNotice" :class="ui.successBox">{{ saveNotice }}</div>

        <div class="flex items-center gap-3 pt-1">
          <button type="submit" :class="ui.primaryBtn" :disabled="saving">
            <i v-if="saving" class="fas fa-circle-notch animate-spin"></i>
            Save keys
          </button>
          <button
            type="button"
            :class="ui.secondaryBtn"
            :disabled="verifying || !settings?.stripe_secret_key_set"
            @click="verify"
          >
            <i :class="['fas', verifying ? 'fa-circle-notch animate-spin' : 'fa-plug-circle-bolt']" class="text-xs"></i>
            Test connection
          </button>
        </div>
      </form>

      <!-- Verify result -->
      <div v-if="verifyError" class="mt-5" :class="ui.errorBox">{{ verifyError }}</div>
      <div v-else-if="verifyResult" class="mt-5" :class="ui.successBox">
        <p class="font-medium mb-1">
          Connected to “{{ verifyResult.account_name || verifyResult.account_email || 'your Stripe account' }}”.
        </p>
        <p v-if="!verifyResult.charges_enabled" class="text-xs opacity-80">
          Heads up: this account can't take charges yet — finish activating it in the Stripe dashboard.
        </p>
        <p v-else class="text-xs opacity-80">Charges are enabled — you're ready to sell.</p>
      </div>
    </section>

    <!-- General -->
    <section class="p-6" :class="ui.card">
      <h2 :class="ui.panelHeading" class="mb-5">Payments</h2>
      <form class="space-y-5" @submit.prevent="saveGeneral">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label :class="ui.label" for="sell-currency">Currency</label>
            <select id="sell-currency" v-model="general.currency" :class="ui.input">
              <option value="usd">USD — US Dollar</option>
              <option value="eur">EUR — Euro</option>
              <option value="gbp">GBP — British Pound</option>
              <option value="cad">CAD — Canadian Dollar</option>
              <option value="aud">AUD — Australian Dollar</option>
            </select>
            <p :class="ui.hintText" class="mt-1.5">Used for every price and checkout.</p>
          </div>
          <div>
            <label :class="ui.label" for="sell-app-url">Your app's address <span class="normal-case tracking-normal font-normal">(once published)</span></label>
            <input id="sell-app-url" v-model="general.app_url" type="url" placeholder="https://yourbusiness.com" :class="ui.input" />
            <p :class="ui.hintText" class="mt-1.5">Stripe only sends customers back to this address after they pay.</p>
          </div>
        </div>
        <div v-if="generalError" :class="ui.errorBox">{{ generalError }}</div>
        <div v-if="generalNotice" :class="ui.successBox">{{ generalNotice }}</div>
        <button type="submit" :class="ui.secondaryBtn" :disabled="savingGeneral">
          <i v-if="savingGeneral" class="fas fa-circle-notch animate-spin text-xs"></i>
          Save
        </button>
      </form>
    </section>
    </div>

    <div class="space-y-6">
      <!-- Server key -->
      <section class="p-6" :class="ui.card">
        <h2 :class="ui.panelHeading" class="mb-1.5">Server key</h2>
        <p :class="ui.bodyText" class="mb-4">
          Lets your app's server report pay-as-you-go usage and check a customer's plan.
          Imagi hands it to your app when it runs it; copy it only if you host the app elsewhere.
        </p>
        <div v-if="serverKey" class="flex items-center gap-2 mb-3">
          <code class="flex-1 px-3 py-2 rounded-lg bg-ink/[0.04] dark:bg-white/[0.06] border border-ink/10 dark:border-white/[0.08] font-mono text-[11px] text-ink/80 dark:text-bone/80 break-all">{{ serverKey }}</code>
          <button :class="ui.iconBtn" type="button" class="w-8 h-8 shrink-0" title="Copy" @click="copy(serverKey)">
            <i :class="['fas', copied === serverKey ? 'fa-check' : 'fa-copy']" class="text-xs"></i>
          </button>
        </div>
        <div class="flex flex-wrap gap-3">
          <button v-if="settings?.server_key_set && !serverKey" type="button" :class="ui.secondaryBtn" @click="revealKey">Show key</button>
          <button type="button" :class="ui.secondaryBtn" :disabled="rotating" @click="rotateKey">
            {{ settings?.server_key_set ? 'Make a new key' : 'Create key' }}
          </button>
        </div>
        <p v-if="settings?.server_key_set" :class="ui.hintText" class="mt-3">A new key stops the old one working right away.</p>
        <div v-if="keyError" class="mt-3" :class="ui.errorBox">{{ keyError }}</div>
      </section>

      <!-- Webhook (own API keys only; Connect updates arrive on Imagi's endpoint) -->
      <section v-if="settings?.connection_type !== 'connect'" class="p-6" :class="ui.card">
        <h2 :class="ui.panelHeading" class="mb-1.5">Webhook</h2>
        <p :class="ui.bodyText" class="mb-4">
          Stripe pushes payment confirmations to this endpoint so orders update on their own.
        </p>

        <template v-if="settings?.stripe_webhook_url">
          <span :class="ui.label">Endpoint URL</span>
          <div class="flex items-center gap-2">
            <code class="flex-1 px-3 py-2 rounded-lg bg-ink/[0.04] dark:bg-white/[0.06] border border-ink/10 dark:border-white/[0.08] font-mono text-[11px] text-ink/80 dark:text-bone/80 break-all">{{ settings.stripe_webhook_url }}</code>
            <button
              :class="ui.iconBtn"
              type="button"
              class="w-8 h-8 shrink-0"
              title="Copy"
              @click="copy(settings.stripe_webhook_url)"
            >
              <i :class="['fas', copied === settings.stripe_webhook_url ? 'fa-check' : 'fa-copy']" class="text-xs"></i>
            </button>
          </div>
          <p :class="ui.hintText" class="mt-2">
            In Stripe: Developers → Webhooks → Add endpoint. Subscribe to
            <code class="font-mono">checkout.session.completed</code>,
            <code class="font-mono">checkout.session.expired</code>, and
            <code class="font-mono">charge.refunded</code>, then paste the signing
            secret (whsec_…) into the form here.
          </p>
        </template>
        <div v-else :class="ui.infoBox">
          The backend has no public URL configured (<code class="font-mono text-xs">SELL_WEBHOOK_BASE_URL</code>),
          so Stripe can't push payment updates yet. Checkouts still work — use
          “Refresh status” on a pending order to pull the payment result from Stripe.
        </div>
      </section>

      <!-- Storefront API -->
      <section class="p-6" :class="ui.card">
        <h2 :class="ui.panelHeading" class="mb-1.5">Storefront API</h2>
        <p :class="ui.bodyText" class="mb-4">
          Your generated app can sell through these endpoints — list products, then send
          customers to Stripe Checkout.
        </p>
        <div class="space-y-4">
          <div>
            <span :class="ui.label">List products</span>
            <code class="block px-3 py-2 rounded-lg bg-ink/[0.04] dark:bg-white/[0.06] border border-ink/10 dark:border-white/[0.08] font-mono text-[11px] text-ink/80 dark:text-bone/80 break-all">GET /api/v1/sell/storefront/{{ store.projectId }}/products/</code>
          </div>
          <div>
            <span :class="ui.label">Start a checkout</span>
            <code class="block px-3 py-2 rounded-lg bg-ink/[0.04] dark:bg-white/[0.06] border border-ink/10 dark:border-white/[0.08] font-mono text-[11px] text-ink/80 dark:text-bone/80 break-all">POST /api/v1/sell/storefront/{{ store.projectId }}/checkout/</code>
            <p :class="ui.hintText" class="mt-1.5">
              Body: <code class="font-mono">{"items": [{"product_id": 1, "quantity": 2}]}</code> →
              returns a <code class="font-mono">checkout_url</code> to redirect the customer to.
            </p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { statusTones } from '@/shared/styles'
import { extractError } from '../services/sellService'
import { useSellStore } from '../stores/sell'
import type { VerifyResult } from '../types'
import { ui } from '../utils/ui'

const route = useRoute()
const store = useSellStore()

const settings = computed(() => store.settings)

const form = reactive({
  stripe_publishable_key: '',
  stripe_secret_key: '',
  stripe_webhook_secret: '',
})

const general = reactive({ currency: 'usd', app_url: '' })
const savingGeneral = ref(false)
const generalError = ref('')
const generalNotice = ref('')

const showKeys = ref(false)
const disconnecting = ref(false)
const serverKey = ref('')
const rotating = ref(false)
const keyError = ref('')

const saving = ref(false)
const saveError = ref('')
const saveNotice = ref('')
const verifying = ref(false)
const verifyError = ref('')
const verifyResult = ref<VerifyResult | null>(null)
const copied = ref('')

function syncFormFromSettings() {
  if (!settings.value) return
  form.stripe_publishable_key = settings.value.stripe_publishable_key
  general.currency = settings.value.currency || 'usd'
  general.app_url = settings.value.app_url || ''
  form.stripe_secret_key = ''
  form.stripe_webhook_secret = ''
}

watch(settings, syncFormFromSettings)

async function save() {
  saving.value = true
  saveError.value = ''
  saveNotice.value = ''
  verifyResult.value = null
  verifyError.value = ''
  try {
    await store.saveSettings({
      stripe_publishable_key: form.stripe_publishable_key.trim(),
      // Blank means "keep the stored secret".
      stripe_secret_key: form.stripe_secret_key.trim(),
      stripe_webhook_secret: form.stripe_webhook_secret.trim(),
    })
    saveNotice.value = 'Keys saved.'
    form.stripe_secret_key = ''
    form.stripe_webhook_secret = ''
  } catch (error) {
    saveError.value = extractError(error, 'Could not save settings.')
  } finally {
    saving.value = false
  }
}

async function verify() {
  verifying.value = true
  verifyError.value = ''
  verifyResult.value = null
  saveNotice.value = ''
  try {
    verifyResult.value = await store.verifyConnection()
  } catch (error) {
    verifyError.value = extractError(error, 'Could not verify the connection.')
  } finally {
    verifying.value = false
  }
}

async function saveGeneral() {
  savingGeneral.value = true
  generalError.value = ''
  generalNotice.value = ''
  try {
    await store.saveSettings({ currency: general.currency, app_url: general.app_url.trim() })
    generalNotice.value = 'Saved.'
  } catch (error) {
    generalError.value = extractError(error, 'Could not save.')
  } finally {
    savingGeneral.value = false
  }
}

async function refreshConnect() {
  verifying.value = true
  verifyError.value = ''
  try {
    await store.refreshConnect()
  } catch (error) {
    verifyError.value = extractError(error, 'Could not check your Stripe account.')
  } finally {
    verifying.value = false
  }
}

async function disconnect() {
  if (!window.confirm('Disconnect this Stripe account? Your app stops taking payments until you connect again. The Stripe account and its money stay yours.')) return
  disconnecting.value = true
  verifyError.value = ''
  try {
    await store.disconnect()
  } catch (error) {
    verifyError.value = extractError(error, 'Could not disconnect.')
  } finally {
    disconnecting.value = false
  }
}

async function revealKey() {
  keyError.value = ''
  try {
    serverKey.value = await store.getServerKey()
  } catch (error) {
    keyError.value = extractError(error, 'Could not load the key.')
  }
}

async function rotateKey() {
  if (settings.value?.server_key_set && !window.confirm('Make a new server key? The old one stops working right away.')) return
  rotating.value = true
  keyError.value = ''
  try {
    serverKey.value = await store.rotateServerKey()
  } catch (error) {
    keyError.value = extractError(error, 'Could not make a key.')
  } finally {
    rotating.value = false
  }
}

async function copy(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    copied.value = text
    setTimeout(() => { copied.value = '' }, 1500)
  } catch {
    // Clipboard unavailable (e.g. http) — the URL is selectable either way.
  }
}

onMounted(async () => {
  if (!settings.value) {
    try {
      await store.fetchSettings()
    } catch (error) {
      saveError.value = extractError(error, 'Could not load settings.')
    }
  }
  syncFormFromSettings()
})
</script>
