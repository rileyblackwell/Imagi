<!--
  SellSettings.vue - Connect the project's Stripe account: API keys, currency,
  webhook signing secret, storefront API endpoints, and a connection test.
-->
<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
    <!-- Credentials form -->
    <section class="lg:col-span-2 p-6" :class="ui.card">
      <div class="flex items-center gap-3 mb-1.5">
        <h2 class="text-base font-semibold text-blue-950 dark:text-white">Stripe account</h2>
        <span
          v-if="settings?.is_configured"
          class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border border-emerald-200/80 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-500/10 text-[11px] font-semibold uppercase tracking-[0.1em] text-emerald-700 dark:text-emerald-300"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-current"></span>
          Connected
        </span>
      </div>
      <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-6">
        Find these under
        <a href="https://dashboard.stripe.com/apikeys" target="_blank" rel="noopener noreferrer" class="rounded-sm font-medium text-blue-950/80 dark:text-blue-100/80 hover:text-blue-950 dark:hover:text-white underline underline-offset-2 decoration-blue-950/30 dark:decoration-blue-100/30 hover:decoration-blue-950/60 dark:hover:decoration-blue-100/70 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]">Developers → API keys</a>
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
          <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1.5">
            Stored encrypted and never shown again. Leave blank to keep the saved key.
          </p>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
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
            <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1.5">Lets Stripe push payment updates to Imagi.</p>
          </div>
          <div>
            <label :class="ui.label" for="sell-currency">Currency</label>
            <select id="sell-currency" v-model="form.currency" :class="ui.input">
              <option value="usd">USD — US Dollar</option>
              <option value="eur">EUR — Euro</option>
              <option value="gbp">GBP — British Pound</option>
              <option value="cad">CAD — Canadian Dollar</option>
              <option value="aud">AUD — Australian Dollar</option>
            </select>
            <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1.5">Used for every product and checkout.</p>
          </div>
        </div>

        <div v-if="saveError" :class="ui.errorBox">{{ saveError }}</div>
        <div v-if="saveNotice" :class="ui.successBox">{{ saveNotice }}</div>

        <div class="flex items-center gap-3 pt-1">
          <button type="submit" :class="ui.primaryBtn" :disabled="saving">
            <i v-if="saving" class="fas fa-circle-notch animate-spin"></i>
            Save settings
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

    <div class="space-y-6">
      <!-- Webhook -->
      <section class="p-6" :class="ui.card">
        <h2 class="text-base font-semibold text-blue-950 dark:text-white mb-1.5">Webhook</h2>
        <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-4">
          Stripe pushes payment confirmations to this endpoint so orders update on their own.
        </p>

        <template v-if="settings?.stripe_webhook_url">
          <span :class="ui.label">Endpoint URL</span>
          <div class="flex items-center gap-2">
            <code class="flex-1 px-3 py-2 rounded-lg bg-blue-950/[0.04] dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.08] font-mono text-[11px] text-blue-950/80 dark:text-blue-100/80 break-all">{{ settings.stripe_webhook_url }}</code>
            <button
              type="button"
              class="w-8 h-8 shrink-0 rounded-lg flex items-center justify-center text-blue-950/50 dark:text-blue-100/50 hover:text-blue-950 dark:hover:text-white hover:bg-blue-50 dark:hover:bg-white/[0.08] transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
              title="Copy"
              @click="copy(settings.stripe_webhook_url)"
            >
              <i :class="['fas', copied === settings.stripe_webhook_url ? 'fa-check' : 'fa-copy']" class="text-xs"></i>
            </button>
          </div>
          <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-2">
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
        <h2 class="text-base font-semibold text-blue-950 dark:text-white mb-1.5">Storefront API</h2>
        <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-4">
          Your generated app can sell through these endpoints — list products, then send
          customers to Stripe Checkout.
        </p>
        <div class="space-y-4">
          <div>
            <span :class="ui.label">List products</span>
            <code class="block px-3 py-2 rounded-lg bg-blue-950/[0.04] dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.08] font-mono text-[11px] text-blue-950/80 dark:text-blue-100/80 break-all">GET /api/v1/sell/storefront/{{ store.projectId }}/products/</code>
          </div>
          <div>
            <span :class="ui.label">Start a checkout</span>
            <code class="block px-3 py-2 rounded-lg bg-blue-950/[0.04] dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.08] font-mono text-[11px] text-blue-950/80 dark:text-blue-100/80 break-all">POST /api/v1/sell/storefront/{{ store.projectId }}/checkout/</code>
            <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1.5">
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
import { extractError } from '../services/sellService'
import { useSellStore } from '../stores/sell'
import type { VerifyResult } from '../types'
import { ui } from '../utils/ui'

const store = useSellStore()

const settings = computed(() => store.settings)

const form = reactive({
  stripe_publishable_key: '',
  stripe_secret_key: '',
  stripe_webhook_secret: '',
  currency: 'usd',
})

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
  form.currency = settings.value.currency || 'usd'
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
      currency: form.currency,
      // Blank means "keep the stored secret".
      stripe_secret_key: form.stripe_secret_key.trim(),
      stripe_webhook_secret: form.stripe_webhook_secret.trim(),
    })
    saveNotice.value = 'Settings saved.'
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
