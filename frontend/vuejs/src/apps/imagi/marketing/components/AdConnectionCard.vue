<!--
  AdConnectionCard.vue - Connect one ad platform (Google Ads or Meta Ads):
  account ID + API credentials, verify, and disconnect. Secrets are write-only;
  the card only shows WHICH credentials are saved, never their values.
-->
<template>
  <section class="p-6" :class="ui.card">
    <div class="flex items-center gap-3 mb-1.5">
      <div class="w-9 h-9 text-sm shrink-0" :class="ui.iconTile">
        <i :class="meta.icon"></i>
      </div>
      <h2 class="text-base font-semibold text-blue-950 dark:text-white">{{ meta.label }}</h2>
      <span
        v-if="connection?.is_configured"
        class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border border-emerald-200/80 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-500/10 text-[11px] font-semibold uppercase tracking-[0.1em] text-emerald-700 dark:text-emerald-300"
      >
        <span class="w-1.5 h-1.5 rounded-full bg-current"></span>
        Connected
      </span>
    </div>
    <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-5">
      {{ description }}
      <a :href="docsUrl" target="_blank" rel="noopener noreferrer" class="text-blue-700 dark:text-blue-300 hover:underline rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0c0c0e]">Setup guide</a>.
    </p>

    <p v-if="connection?.account_name" class="text-xs text-blue-950/50 dark:text-blue-100/50 mb-4 -mt-2">
      Verified as “{{ connection.account_name }}”
      <template v-if="connection.currency">({{ connection.currency }})</template>
      <template v-if="connection.last_verified_at"> · {{ formatDateTime(connection.last_verified_at) }}</template>
    </p>

    <form class="space-y-4" @submit.prevent="save">
      <div v-for="field in fields" :key="field.key">
        <label :class="ui.label" :for="`${provider}-${field.key}`">
          {{ field.label }}
          <span v-if="field.optional" class="normal-case tracking-normal font-normal">(optional)</span>
        </label>
        <input
          :id="`${provider}-${field.key}`"
          v-model="form[field.key]"
          :type="field.secret ? 'password' : 'text'"
          :placeholder="placeholderFor(field)"
          autocomplete="off"
          spellcheck="false"
          class="font-mono text-xs"
          :class="ui.input"
        />
        <p v-if="field.hint" class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1.5">{{ field.hint }}</p>
      </div>

      <div v-if="error" :class="ui.errorBox">{{ error }}</div>
      <div v-if="notice" :class="ui.successBox">{{ notice }}</div>

      <div class="flex flex-wrap items-center gap-3 pt-1">
        <button type="submit" :class="ui.primaryBtn" :disabled="saving">
          <i v-if="saving" class="fas fa-circle-notch animate-spin motion-reduce:animate-none"></i>
          Save
        </button>
        <button
          type="button"
          :class="ui.secondaryBtn"
          :disabled="verifying || !connection?.is_configured"
          @click="verify"
        >
          <i :class="['fas', verifying ? 'fa-circle-notch animate-spin motion-reduce:animate-none' : 'fa-plug-circle-bolt']" class="text-xs"></i>
          Test connection
        </button>
        <button
          v-if="connection?.is_configured || connection?.credentials_set.length"
          type="button"
          :class="ui.dangerBtn"
          :disabled="disconnecting"
          @click="disconnect"
        >
          <i :class="['fas', disconnecting ? 'fa-circle-notch animate-spin motion-reduce:animate-none' : 'fa-link-slash']" class="text-xs"></i>
          Disconnect
        </button>
      </div>
    </form>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { extractError } from '../services/marketingService'
import { useMarketingStore } from '../stores/marketing'
import type { AdProvider } from '../types'
import { AD_PROVIDERS, formatDateTime, ui } from '../utils/ui'

interface Field {
  key: string
  label: string
  secret?: boolean
  optional?: boolean
  placeholder?: string
  hint?: string
}

const props = defineProps<{
  provider: AdProvider
}>()

const store = useMarketingStore()

const meta = computed(() => AD_PROVIDERS[props.provider])

const connection = computed(
  () => store.adConnections.find(c => c.provider === props.provider) || null
)

const FIELDS: Record<AdProvider, Field[]> = {
  meta: [
    {
      key: 'account_id',
      label: 'Ad account ID',
      placeholder: 'act_1234567890 or 1234567890',
      hint: 'Found in Meta Ads Manager under Account overview.',
    },
    {
      key: 'access_token',
      label: 'Access token',
      secret: true,
      hint: 'A system-user token with ads_management permission, from Meta Business settings.',
    },
  ],
  google: [
    {
      key: 'account_id',
      label: 'Customer ID',
      placeholder: '123-456-7890',
      hint: 'Shown in the top-right of the Google Ads console.',
    },
    { key: 'developer_token', label: 'Developer token', secret: true },
    { key: 'client_id', label: 'OAuth client ID', placeholder: '….apps.googleusercontent.com' },
    { key: 'client_secret', label: 'OAuth client secret', secret: true },
    {
      key: 'refresh_token',
      label: 'OAuth refresh token',
      secret: true,
      hint: 'Generated once for your Google account with the AdWords scope.',
    },
    {
      key: 'login_customer_id',
      label: 'Manager (MCC) customer ID',
      optional: true,
      hint: 'Only when access goes through a manager account.',
    },
  ],
}

const fields = computed(() => FIELDS[props.provider])

const description = computed(() =>
  props.provider === 'meta'
    ? 'Sync Facebook and Instagram ad campaigns and control them from Imagi.'
    : 'Sync Google Search, Display, and YouTube campaigns and control them from Imagi.'
)

const docsUrl = computed(() =>
  props.provider === 'meta'
    ? 'https://developers.facebook.com/docs/marketing-api/get-started'
    : 'https://developers.google.com/google-ads/api/docs/get-started/introduction'
)

const form = reactive<Record<string, string>>({})
const saving = ref(false)
const verifying = ref(false)
const disconnecting = ref(false)
const error = ref('')
const notice = ref('')

function syncFormFromConnection() {
  for (const field of fields.value) {
    form[field.key] = field.key === 'account_id' ? (connection.value?.account_id ?? '') : ''
  }
}

watch(connection, syncFormFromConnection, { immediate: true })

function placeholderFor(field: Field): string {
  if (field.secret && connection.value?.credentials_set.includes(field.key)) {
    return '•••••••• saved — enter a new value to replace it'
  }
  return field.placeholder ?? ''
}

function resetMessages() {
  error.value = ''
  notice.value = ''
}

async function save() {
  saving.value = true
  resetMessages()
  try {
    await store.saveAdConnection(props.provider, { ...form })
    notice.value = 'Saved. Test the connection to verify the credentials.'
    syncFormFromConnection()
  } catch (err) {
    error.value = extractError(err, 'Could not save the connection.')
  } finally {
    saving.value = false
  }
}

async function verify() {
  verifying.value = true
  resetMessages()
  try {
    const result = await store.verifyAdConnection(props.provider)
    notice.value = `Connected to “${result.connection.account_name || 'your account'}”.`
  } catch (err) {
    error.value = extractError(err, 'Could not verify the connection.')
  } finally {
    verifying.value = false
  }
}

async function disconnect() {
  if (!window.confirm(`Disconnect ${meta.value.label}? Stored credentials and synced campaigns are removed from Imagi (nothing changes on the platform).`)) {
    return
  }
  disconnecting.value = true
  resetMessages()
  try {
    await store.disconnectAdProvider(props.provider)
    syncFormFromConnection()
    notice.value = 'Disconnected.'
  } catch (err) {
    error.value = extractError(err, 'Could not disconnect.')
  } finally {
    disconnecting.value = false
  }
}
</script>
