<!--
  MarketingCampaignDetail.vue - One campaign.

  Drafts show the composer: edit the message/audience, see how many contacts
  it will reach, then send now or schedule. Sent/scheduled campaigns show the
  delivery report with per-recipient statuses and sync/cancel actions.
-->
<template>
  <div>
    <router-link
      :to="{ name: 'marketing-campaigns', params: { projectName: route.params.projectName } }"
      class="inline-flex items-center gap-2 text-sm font-medium text-blue-950/60 dark:text-blue-100/60 hover:text-blue-950 dark:hover:text-white transition-colors duration-200 mb-5"
    >
      <i class="fas fa-arrow-left text-xs"></i>
      <span>All campaigns</span>
    </router-link>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-violet-200 dark:border-violet-300/30 border-t-violet-600 dark:border-t-violet-300 rounded-full animate-spin"></div>
    </div>

    <div v-else-if="loadError" :class="ui.errorBox">{{ loadError }}</div>

    <template v-else-if="campaign">
      <!-- Header -->
      <section class="flex flex-col sm:flex-row sm:items-center gap-4 mb-6">
        <div class="w-12 h-12 shrink-0" :class="ui.iconTile">
          <i :class="['fas', campaign.channel === 'voice' ? 'fa-phone-volume' : 'fa-comment-sms']"></i>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex flex-wrap items-center gap-3">
            <h1 class="text-2xl font-semibold text-blue-950 dark:text-white tracking-tight truncate">{{ campaign.name }}</h1>
            <StatusBadge :status="campaign.status" />
          </div>
          <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mt-1">
            {{ campaign.channel === 'voice' ? 'Voice broadcast' : 'SMS campaign' }}
            <template v-if="campaign.scheduled_at"> · scheduled for {{ formatDateTime(campaign.scheduled_at) }}</template>
            <template v-else-if="campaign.completed_at"> · finished {{ formatDateTime(campaign.completed_at) }}</template>
          </p>
        </div>
        <div class="flex items-center gap-2.5 shrink-0">
          <button
            v-if="campaign.status === 'scheduled' || campaign.status === 'sending'"
            type="button"
            :class="ui.secondaryBtn"
            :disabled="acting"
            @click="sync"
          >
            <i class="fas fa-rotate text-xs" :class="{ 'animate-spin': acting }"></i>
            Refresh statuses
          </button>
          <button
            v-else-if="campaign.status === 'sent'"
            type="button"
            :class="ui.secondaryBtn"
            :disabled="acting"
            @click="sync"
          >
            <i class="fas fa-rotate text-xs" :class="{ 'animate-spin': acting }"></i>
            Refresh statuses
          </button>
          <button
            v-if="campaign.status === 'scheduled'"
            type="button"
            :class="ui.dangerBtn"
            :disabled="acting"
            @click="cancel"
          >
            Cancel send
          </button>
          <button
            v-if="campaign.status !== 'sending' && campaign.status !== 'scheduled'"
            type="button"
            :class="ui.dangerBtn"
            :disabled="acting"
            @click="remove"
          >
            <i class="fas fa-trash-can text-xs"></i>
            Delete
          </button>
        </div>
      </section>

      <div v-if="actionError" class="mb-5" :class="ui.errorBox">{{ actionError }}</div>
      <div v-if="actionNotice" class="mb-5" :class="ui.successBox">{{ actionNotice }}</div>

      <!-- DRAFT: composer -->
      <template v-if="campaign.status === 'draft'">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <section class="lg:col-span-2 p-6" :class="ui.card">
            <h2 class="text-base font-semibold text-blue-950 dark:text-white mb-5">Compose</h2>
            <CampaignForm
              :key="campaign.updated_at"
              :initial="campaign"
              :tags="store.tags"
              :busy="saving"
              :error="saveError"
              submit-label="Save changes"
              @submit="save"
              @cancel="router.back()"
            />
          </section>

          <div class="space-y-6">
            <!-- Audience preview -->
            <section class="p-6" :class="ui.card">
              <h2 class="text-base font-semibold text-blue-950 dark:text-white mb-3">Audience</h2>
              <p class="text-3xl font-semibold text-blue-950 dark:text-white tabular-nums mb-1">
                {{ recipientCount === null ? '—' : recipientCount.toLocaleString() }}
              </p>
              <p class="text-sm text-blue-950/60 dark:text-blue-100/60">
                subscribed contact{{ recipientCount === 1 ? '' : 's' }} will receive this
                {{ campaign.channel === 'voice' ? 'call' : 'message' }}
              </p>
              <p v-if="recipientCount === 0" class="text-xs text-amber-700 dark:text-amber-300 mt-2">
                Add contacts in the Audience tab first, or adjust the tags.
              </p>
            </section>

            <!-- Send -->
            <section class="p-6" :class="ui.card">
              <h2 class="text-base font-semibold text-blue-950 dark:text-white mb-4">Send</h2>
              <button
                type="button"
                class="w-full mb-4"
                :class="ui.primaryBtn"
                :disabled="acting || recipientCount === 0 || !store.isConfigured"
                @click="sendNow"
              >
                <i class="fas fa-paper-plane text-xs"></i>
                Send now
              </button>

              <div class="pt-4 border-t border-blue-200/60 dark:border-white/[0.1]">
                <label :class="ui.label" for="schedule-time">Or schedule for later</label>
                <input
                  id="schedule-time"
                  v-model="scheduleAt"
                  type="datetime-local"
                  :class="ui.input"
                  :disabled="!canSchedule"
                />
                <button
                  type="button"
                  class="w-full mt-3"
                  :class="ui.secondaryBtn"
                  :disabled="acting || !scheduleAt || recipientCount === 0 || !canSchedule"
                  @click="schedule"
                >
                  <i class="fas fa-clock text-xs"></i>
                  Schedule
                </button>
                <p v-if="!canSchedule" class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-2.5">
                  Scheduling is handled by Twilio and needs a Messaging Service SID —
                  add one in Settings. SMS only, 15 minutes to 35 days out.
                </p>
                <p v-else class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-2.5">
                  Twilio delivers scheduled campaigns even if Imagi is offline. 15 minutes to 35 days out.
                </p>
              </div>
              <p v-if="!store.isConfigured" class="text-xs text-amber-700 dark:text-amber-300 mt-3">
                Connect Twilio in Settings before sending.
              </p>
            </section>
          </div>
        </div>
      </template>

      <!-- SENT / SCHEDULED / FAILED: report -->
      <template v-else>
        <!-- Stats -->
        <section class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div v-for="stat in reportStats" :key="stat.label" class="p-5" :class="ui.card">
            <p class="text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50 mb-2">{{ stat.label }}</p>
            <p class="text-2xl font-semibold tabular-nums" :class="stat.tone">{{ stat.value }}</p>
          </div>
        </section>

        <!-- Message body -->
        <section class="p-6 mb-6" :class="ui.card">
          <h2 class="text-sm font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50 mb-3">
            {{ campaign.channel === 'voice' ? 'Voice script' : 'Message' }}
          </h2>
          <p class="text-sm text-blue-950 dark:text-white whitespace-pre-wrap">{{ campaign.body }}</p>
        </section>

        <!-- Recipients -->
        <section class="p-6" :class="ui.card">
          <h2 class="text-base font-semibold text-blue-950 dark:text-white mb-4">Recipients</h2>
          <div v-if="messages.length" class="overflow-x-auto -mx-2">
            <table class="w-full text-sm min-w-[560px]">
              <thead>
                <tr class="text-left text-xs font-semibold uppercase tracking-[0.12em] text-blue-950/50 dark:text-blue-100/50">
                  <th class="px-2 py-2.5 font-semibold">Contact</th>
                  <th class="px-2 py-2.5 font-semibold">Number</th>
                  <th class="px-2 py-2.5 font-semibold">Status</th>
                  <th class="px-2 py-2.5 font-semibold">Detail</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="message in messages"
                  :key="message.id"
                  class="border-t border-blue-200/50 dark:border-white/[0.06]"
                >
                  <td class="px-2 py-3 text-blue-950 dark:text-white font-medium">{{ message.contact_name || '—' }}</td>
                  <td class="px-2 py-3 text-blue-950/70 dark:text-blue-100/70 font-mono text-xs">{{ message.to_number }}</td>
                  <td class="px-2 py-3"><StatusBadge :status="message.status" /></td>
                  <td class="px-2 py-3 text-xs text-blue-950/60 dark:text-blue-100/60">
                    {{ message.error_message || (message.error_code ? `Error ${message.error_code}` : '—') }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="text-sm text-blue-950/60 dark:text-blue-100/60 py-6 text-center">No messages recorded for this campaign.</p>
        </section>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CampaignForm from '../components/CampaignForm.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { extractError } from '../services/marketingService'
import { useMarketingStore } from '../stores/marketing'
import type { Campaign, CampaignPayload, Message } from '../types'
import { formatDateTime, ui } from '../utils/ui'

const route = useRoute()
const router = useRouter()
const store = useMarketingStore()

const campaign = ref<Campaign | null>(null)
const messages = ref<Message[]>([])
const recipientCount = ref<number | null>(null)
const loading = ref(true)
const loadError = ref('')
const saving = ref(false)
const saveError = ref('')
const acting = ref(false)
const actionError = ref('')
const actionNotice = ref('')
const scheduleAt = ref('')

const campaignId = computed(() => Number(route.params.campaignId))

const canSchedule = computed(() =>
  campaign.value?.channel === 'sms'
  && Boolean(store.settings?.twilio_messaging_service_sid)
)

const reportStats = computed(() => {
  const stats = campaign.value?.stats
  if (!stats) return []
  const ink = 'text-blue-950 dark:text-white'
  return [
    { label: 'Recipients', value: stats.recipients.toLocaleString(), tone: ink },
    { label: 'Delivered', value: stats.delivered.toLocaleString(), tone: 'text-emerald-600 dark:text-emerald-300' },
    { label: 'Pending', value: stats.pending.toLocaleString(), tone: ink },
    { label: 'Failed', value: stats.failed.toLocaleString(), tone: stats.failed ? 'text-red-600 dark:text-red-300' : ink },
  ]
})

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    const detail = await store.getCampaign(campaignId.value)
    campaign.value = detail.campaign
    messages.value = detail.messages
    if (detail.campaign.status === 'draft') {
      await Promise.all([
        refreshRecipients(),
        store.tags.length ? Promise.resolve() : store.fetchTags().catch(() => {}),
      ])
    }
  } catch (error) {
    loadError.value = extractError(error, 'Could not load this campaign.')
  } finally {
    loading.value = false
  }
}

async function refreshRecipients() {
  try {
    recipientCount.value = await store.previewRecipients(campaignId.value)
  } catch {
    recipientCount.value = null
  }
}

async function save(payload: CampaignPayload) {
  saving.value = true
  saveError.value = ''
  actionNotice.value = ''
  try {
    campaign.value = await store.updateCampaign(campaignId.value, payload)
    actionNotice.value = 'Draft saved.'
    await refreshRecipients()
  } catch (error) {
    saveError.value = extractError(error, 'Could not save the campaign.')
  } finally {
    saving.value = false
  }
}

async function sendNow() {
  if (!campaign.value) return
  const count = recipientCount.value ?? 0
  const noun = campaign.value.channel === 'voice' ? 'call' : 'message'
  if (!window.confirm(`Send this ${noun} to ${count} contact${count === 1 ? '' : 's'} now?`)) return
  await runAction(async () => {
    const result = await store.sendCampaign(campaignId.value)
    actionNotice.value = result.failed
      ? `Dispatched ${result.dispatched}, ${result.failed} failed — see recipient details below.`
      : `Campaign sent to ${result.dispatched} contact${result.dispatched === 1 ? '' : 's'}.`
  })
}

async function schedule() {
  if (!scheduleAt.value) return
  const sendAt = new Date(scheduleAt.value)
  if (Number.isNaN(sendAt.getTime())) {
    actionError.value = 'Enter a valid date and time.'
    return
  }
  await runAction(async () => {
    await store.sendCampaign(campaignId.value, sendAt.toISOString())
    actionNotice.value = `Campaign scheduled — Twilio will deliver it ${formatDateTime(sendAt.toISOString())}.`
  })
}

async function cancel() {
  if (!window.confirm('Cancel this scheduled campaign? Messages not yet sent will be canceled.')) return
  await runAction(async () => {
    await store.cancelCampaign(campaignId.value)
    actionNotice.value = 'Campaign canceled.'
  })
}

async function sync() {
  await runAction(async () => {
    const result = await store.syncCampaign(campaignId.value)
    actionNotice.value = result.updated
      ? `Updated ${result.updated} message status${result.updated === 1 ? '' : 'es'} from Twilio.`
      : 'Statuses are up to date.'
  })
}

async function remove() {
  if (!campaign.value) return
  if (!window.confirm(`Delete "${campaign.value.name}"? This also removes its delivery history.`)) return
  acting.value = true
  actionError.value = ''
  try {
    await store.deleteCampaign(campaignId.value)
    router.push({ name: 'marketing-campaigns', params: { projectName: String(route.params.projectName) } })
  } catch (error) {
    actionError.value = extractError(error, 'Could not delete the campaign.')
  } finally {
    acting.value = false
  }
}

/** Run a send/cancel/sync action, then reload the campaign + messages. */
async function runAction(action: () => Promise<void>) {
  acting.value = true
  actionError.value = ''
  actionNotice.value = ''
  try {
    await action()
    const detail = await store.getCampaign(campaignId.value)
    campaign.value = detail.campaign
    messages.value = detail.messages
  } catch (error) {
    actionError.value = extractError(error, 'The action failed.')
  } finally {
    acting.value = false
  }
}

onMounted(load)
watch(campaignId, load)
</script>
