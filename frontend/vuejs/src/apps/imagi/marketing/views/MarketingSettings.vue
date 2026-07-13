<!--
  MarketingSettings.vue - Connect the project's marketing accounts: the Twilio
  account for messaging (credentials, sender number, webhooks, connection test)
  and the Google Ads / Meta Ads accounts for the ads dashboard.
-->
<template>
  <div>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
    <!-- Credentials form -->
    <section class="lg:col-span-2 p-6" :class="ui.card">
      <div class="flex items-center gap-3 mb-1.5">
        <h2 class="text-base font-semibold text-blue-950 dark:text-white">Twilio account</h2>
        <span
          v-if="settings?.is_configured"
          class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border border-emerald-200/80 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-500/10 text-[11px] font-semibold uppercase tracking-[0.1em] text-emerald-700 dark:text-emerald-300"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-current"></span>
          Connected
        </span>
      </div>
      <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-6">
        Find these in the
        <a href="https://console.twilio.com" target="_blank" rel="noopener noreferrer" class="text-violet-700 dark:text-violet-300 hover:underline">Twilio Console</a>.
        Messages and calls are sent from your own Twilio account.
      </p>

      <form class="space-y-5" @submit.prevent="save">
        <div>
          <label :class="ui.label" for="twilio-sid">Account SID</label>
          <input
            id="twilio-sid"
            v-model="form.twilio_account_sid"
            type="text"
            placeholder="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
            autocomplete="off"
            spellcheck="false"
            class="font-mono text-xs"
            :class="ui.input"
          />
        </div>
        <div>
          <label :class="ui.label" for="twilio-token">Auth token</label>
          <input
            id="twilio-token"
            v-model="form.twilio_auth_token"
            type="password"
            autocomplete="new-password"
            :placeholder="settings?.twilio_auth_token_set ? '•••••••• saved — enter a new token to replace it' : 'Your Twilio auth token'"
            class="font-mono text-xs"
            :class="ui.input"
          />
          <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1.5">
            Stored encrypted and never shown again. Leave blank to keep the saved token.
          </p>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div>
            <label :class="ui.label" for="twilio-phone">Twilio phone number</label>
            <input
              id="twilio-phone"
              v-model="form.twilio_phone_number"
              type="tel"
              placeholder="+15551234567"
              class="font-mono text-xs"
              :class="ui.input"
            />
            <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1.5">The sender for your messages and calls.</p>
          </div>
          <div>
            <label :class="ui.label" for="twilio-msid">Messaging Service SID <span class="normal-case tracking-normal font-normal">(optional)</span></label>
            <input
              id="twilio-msid"
              v-model="form.twilio_messaging_service_sid"
              type="text"
              placeholder="MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
              autocomplete="off"
              spellcheck="false"
              class="font-mono text-xs"
              :class="ui.input"
            />
            <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1.5">Required for scheduled campaigns.</p>
          </div>
        </div>
        <div>
          <label :class="ui.label" for="twilio-voice">Voice for calls</label>
          <select id="twilio-voice" v-model="form.voice" :class="ui.input">
            <option value="Polly.Joanna">Joanna — female, US English</option>
            <option value="Polly.Matthew">Matthew — male, US English</option>
            <option value="Polly.Amy">Amy — female, British English</option>
            <option value="Polly.Brian">Brian — male, British English</option>
            <option value="alice">Alice — classic</option>
          </select>
          <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1.5">Text-to-speech voice used for voice broadcasts.</p>
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
            :disabled="verifying || !settings?.twilio_account_sid || !settings?.twilio_auth_token_set"
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
          Connected to “{{ verifyResult.account_name || 'your Twilio account' }}” ({{ verifyResult.account_status }}).
        </p>
        <template v-if="verifyResult.phone_numbers.length">
          <p class="text-xs opacity-80 mb-2">Numbers on this account — click one to use it as your sender:</p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="number in verifyResult.phone_numbers"
              :key="number.phone_number"
              type="button"
              class="px-3 py-1.5 rounded-full border border-emerald-300/70 dark:border-emerald-400/30 bg-white/70 dark:bg-white/[0.06] font-mono text-xs hover:bg-white dark:hover:bg-white/[0.12] transition-colors duration-150"
              @click="useNumber(number.phone_number)"
            >
              {{ number.phone_number }}
            </button>
          </div>
        </template>
        <p v-else class="text-xs opacity-80">No phone numbers on this account yet — buy one in the Twilio Console.</p>
      </div>
    </section>

    <div class="space-y-6">
      <!-- Webhooks -->
      <section class="p-6" :class="ui.card">
        <h2 class="text-base font-semibold text-blue-950 dark:text-white mb-1.5">Webhooks</h2>
        <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-4">
          Twilio pushes delivery updates and incoming texts to these endpoints.
        </p>

        <template v-if="settings?.inbound_webhook_url">
          <div class="space-y-4">
            <div>
              <span :class="ui.label">Incoming messages</span>
              <div class="flex items-center gap-2">
                <code class="flex-1 px-3 py-2 rounded-lg bg-blue-950/[0.04] dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.08] font-mono text-[11px] text-blue-950/80 dark:text-blue-100/80 break-all">{{ settings.inbound_webhook_url }}</code>
                <button
                  type="button"
                  class="w-8 h-8 shrink-0 rounded-lg flex items-center justify-center text-blue-950/50 dark:text-white/50 hover:text-blue-950 dark:hover:text-white hover:bg-blue-50 dark:hover:bg-white/[0.08] transition-colors duration-150"
                  title="Copy"
                  @click="copy(settings.inbound_webhook_url)"
                >
                  <i :class="['fas', copied === settings.inbound_webhook_url ? 'fa-check' : 'fa-copy']" class="text-xs"></i>
                </button>
              </div>
              <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1.5">
                Set as “A message comes in” on your Twilio number to receive replies in the inbox.
              </p>
            </div>
            <div>
              <span :class="ui.label">Delivery status</span>
              <div class="flex items-center gap-2">
                <code class="flex-1 px-3 py-2 rounded-lg bg-blue-950/[0.04] dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.08] font-mono text-[11px] text-blue-950/80 dark:text-blue-100/80 break-all">{{ settings.status_callback_url }}</code>
                <button
                  type="button"
                  class="w-8 h-8 shrink-0 rounded-lg flex items-center justify-center text-blue-950/50 dark:text-white/50 hover:text-blue-950 dark:hover:text-white hover:bg-blue-50 dark:hover:bg-white/[0.08] transition-colors duration-150"
                  title="Copy"
                  @click="copy(settings.status_callback_url)"
                >
                  <i :class="['fas', copied === settings.status_callback_url ? 'fa-check' : 'fa-copy']" class="text-xs"></i>
                </button>
              </div>
              <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1.5">
                Attached automatically to outbound messages — nothing to configure.
              </p>
            </div>
          </div>
        </template>
        <div v-else :class="ui.infoBox">
          The backend has no public URL configured (<code class="font-mono text-xs">MARKETING_WEBHOOK_BASE_URL</code>),
          so delivery receipts and incoming texts can't reach Imagi yet. Campaigns still send —
          use “Refresh statuses” on a campaign to pull delivery updates from Twilio.
        </div>
      </section>

      <!-- Compliance -->
      <section class="p-6" :class="ui.card">
        <h2 class="text-base font-semibold text-blue-950 dark:text-white mb-3">Messaging rules</h2>
        <ul class="space-y-2.5 text-sm text-blue-950/70 dark:text-blue-100/70">
          <li class="flex gap-2.5">
            <i class="fas fa-circle-check text-emerald-600 dark:text-emerald-300 mt-0.5 text-xs"></i>
            Only message people who agreed to hear from your business.
          </li>
          <li class="flex gap-2.5">
            <i class="fas fa-circle-check text-emerald-600 dark:text-emerald-300 mt-0.5 text-xs"></i>
            STOP replies unsubscribe contacts automatically; START re-subscribes them.
          </li>
          <li class="flex gap-2.5">
            <i class="fas fa-circle-check text-emerald-600 dark:text-emerald-300 mt-0.5 text-xs"></i>
            Campaigns only go to subscribed contacts — unsubscribed ones are always skipped.
          </li>
          <li class="flex gap-2.5">
            <i class="fas fa-circle-check text-emerald-600 dark:text-emerald-300 mt-0.5 text-xs"></i>
            US numbers may need
            <a href="https://www.twilio.com/docs/messaging/compliance/a2p-10dlc" target="_blank" rel="noopener noreferrer" class="text-violet-700 dark:text-violet-300 hover:underline">A2P 10DLC registration</a>
            in Twilio for reliable delivery.
          </li>
        </ul>
      </section>
    </div>
  </div>

  <!-- Ad platforms -->
  <div class="mt-10">
    <h2 class="text-lg font-semibold text-blue-950 dark:text-white mb-1.5 transition-colors duration-300">Ad platforms</h2>
    <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-5">
      Connect your ad accounts to watch campaign performance and pause or resume campaigns from the
      <router-link :to="{ name: 'marketing-ads', params: { projectName: route.params.projectName } }" class="text-violet-700 dark:text-violet-300 hover:underline">Ads tab</router-link>.
      Credentials are stored encrypted, and Imagi never creates or edits ads without you.
    </p>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
      <AdConnectionCard provider="google" />
      <AdConnectionCard provider="meta" />
    </div>
  </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import AdConnectionCard from '../components/AdConnectionCard.vue'
import { extractError } from '../services/marketingService'
import { useMarketingStore } from '../stores/marketing'
import type { VerifyResult } from '../types'
import { ui } from '../utils/ui'

const route = useRoute()
const store = useMarketingStore()

const settings = computed(() => store.settings)

const form = reactive({
  twilio_account_sid: '',
  twilio_auth_token: '',
  twilio_phone_number: '',
  twilio_messaging_service_sid: '',
  voice: 'Polly.Joanna',
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
  form.twilio_account_sid = settings.value.twilio_account_sid
  form.twilio_phone_number = settings.value.twilio_phone_number
  form.twilio_messaging_service_sid = settings.value.twilio_messaging_service_sid
  form.voice = settings.value.voice || 'Polly.Joanna'
  form.twilio_auth_token = ''
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
      twilio_account_sid: form.twilio_account_sid.trim(),
      twilio_phone_number: form.twilio_phone_number.trim().replace(/[\s()-]/g, ''),
      twilio_messaging_service_sid: form.twilio_messaging_service_sid.trim(),
      voice: form.voice,
      // Blank means "keep the stored token".
      twilio_auth_token: form.twilio_auth_token.trim(),
    })
    saveNotice.value = 'Settings saved.'
    form.twilio_auth_token = ''
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

async function useNumber(phoneNumber: string) {
  form.twilio_phone_number = phoneNumber
  await save()
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
  if (!store.adConnections.length) {
    try {
      await store.fetchAdConnections()
    } catch (error) {
      console.error('Failed to load ad connections:', error)
    }
  }
})
</script>
