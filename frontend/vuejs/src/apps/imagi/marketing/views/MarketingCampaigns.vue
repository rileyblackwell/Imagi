<!--
  MarketingCampaigns.vue - Campaign list with status filter and a "New
  campaign" modal. Rows link to the campaign detail (composer for drafts,
  delivery report once sent).
-->
<template>
  <div>
    <!-- Toolbar -->
    <div class="flex flex-col sm:flex-row sm:items-center gap-3 mb-6">
      <div class="flex items-center gap-1.5 flex-wrap flex-1">
        <button
          v-for="option in statusFilters"
          :key="option.value"
          type="button"
          class="px-3.5 py-1.5 rounded-full border text-xs font-semibold transition-all duration-200"
          :class="statusFilter === option.value
            ? 'border-violet-300 dark:border-violet-400/50 bg-violet-100/80 dark:bg-violet-400/20 text-violet-800 dark:text-violet-200'
            : 'border-blue-200/70 dark:border-white/[0.12] bg-white dark:bg-white/[0.04] text-blue-950/60 dark:text-blue-100/60 hover:text-blue-950 dark:hover:text-white'"
          @click="setStatusFilter(option.value)"
        >
          {{ option.label }}
        </button>
      </div>
      <button type="button" :class="ui.primaryBtn" @click="showCreate = true">
        <i class="fas fa-plus text-xs"></i>
        New campaign
      </button>
    </div>

    <!-- Loading -->
    <div v-if="store.campaignsLoading && !store.campaigns.length" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-violet-200 dark:border-violet-300/30 border-t-violet-600 dark:border-t-violet-300 rounded-full animate-spin"></div>
    </div>

    <!-- List -->
    <div v-else-if="store.campaigns.length" class="space-y-3">
      <router-link
        v-for="campaign in store.campaigns"
        :key="campaign.id"
        :to="{ name: 'marketing-campaign-detail', params: { projectName: route.params.projectName, campaignId: campaign.id } }"
        class="flex flex-col sm:flex-row sm:items-center gap-4 p-5 group"
        :class="ui.card"
      >
        <div class="flex items-center gap-4 flex-1 min-w-0">
          <div class="w-11 h-11 shrink-0" :class="ui.iconTile">
            <i :class="['fas', campaign.channel === 'voice' ? 'fa-phone-volume' : 'fa-comment-sms']"></i>
          </div>
          <div class="min-w-0">
            <p class="text-base font-semibold text-blue-950 dark:text-white truncate group-hover:text-violet-800 dark:group-hover:text-violet-200 transition-colors duration-200">
              {{ campaign.name }}
            </p>
            <p class="text-sm text-blue-950/60 dark:text-blue-100/60 truncate">{{ campaign.body }}</p>
          </div>
        </div>
        <div class="flex items-center gap-5 shrink-0">
          <div v-if="campaign.status !== 'draft'" class="text-right">
            <p class="text-sm font-semibold text-blue-950 dark:text-white tabular-nums">
              {{ campaign.stats.delivered }}/{{ campaign.stats.recipients }}
            </p>
            <p class="text-xs text-blue-950/50 dark:text-blue-100/50">delivered</p>
          </div>
          <div class="text-right hidden md:block">
            <p class="text-sm text-blue-950/70 dark:text-blue-100/70">{{ formatDateTime(campaign.scheduled_at || campaign.created_at) }}</p>
            <p class="text-xs text-blue-950/50 dark:text-blue-100/50">{{ campaign.scheduled_at ? 'scheduled for' : 'created' }}</p>
          </div>
          <StatusBadge :status="campaign.status" />
          <i class="fas fa-chevron-right text-xs text-blue-950/30 dark:text-white/30 group-hover:translate-x-0.5 transition-transform duration-200"></i>
        </div>
      </router-link>
    </div>

    <!-- Empty -->
    <div v-else class="flex flex-col items-center justify-center py-20 text-center">
      <div class="w-16 h-16 text-2xl mb-5" :class="ui.iconTile">
        <i class="fas fa-paper-plane"></i>
      </div>
      <h2 class="text-xl font-semibold text-blue-950 dark:text-white mb-2">
        {{ statusFilter ? 'No campaigns with this status' : 'No campaigns yet' }}
      </h2>
      <p class="text-sm text-blue-950/60 dark:text-blue-100/60 max-w-md mb-6">
        {{ statusFilter
          ? 'Try a different filter, or create a new campaign.'
          : 'Announce launches, promotions, and updates with an SMS blast or a voice broadcast to your audience.' }}
      </p>
      <button type="button" :class="ui.primaryBtn" @click="showCreate = true">
        <i class="fas fa-plus text-xs"></i>
        Create your first campaign
      </button>
    </div>

    <div v-if="loadError" class="mt-4" :class="ui.errorBox">{{ loadError }}</div>

    <!-- Create modal -->
    <MarketingModal v-if="showCreate" title="New campaign" wide @close="closeCreate">
      <CampaignForm
        :tags="store.tags"
        :busy="creating"
        :error="createError"
        submit-label="Save draft"
        @submit="createCampaign"
        @cancel="closeCreate"
      />
    </MarketingModal>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CampaignForm from '../components/CampaignForm.vue'
import MarketingModal from '../components/MarketingModal.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { extractError } from '../services/marketingService'
import { useMarketingStore } from '../stores/marketing'
import type { CampaignPayload } from '../types'
import { formatDateTime, ui } from '../utils/ui'

const route = useRoute()
const router = useRouter()
const store = useMarketingStore()

const statusFilter = ref('')
const showCreate = ref(route.query.new === '1')
const creating = ref(false)
const createError = ref('')
const loadError = ref('')

const statusFilters = [
  { value: '', label: 'All' },
  { value: 'draft', label: 'Drafts' },
  { value: 'scheduled', label: 'Scheduled' },
  { value: 'sent', label: 'Sent' },
  { value: 'failed', label: 'Failed' },
]

async function load() {
  loadError.value = ''
  try {
    await store.fetchCampaigns(statusFilter.value ? { status: statusFilter.value } : {})
  } catch (error) {
    loadError.value = extractError(error, 'Could not load campaigns.')
  }
}

function setStatusFilter(value: string) {
  statusFilter.value = value
  load()
}

function closeCreate() {
  showCreate.value = false
  createError.value = ''
  if (route.query.new) {
    router.replace({ query: {} })
  }
}

async function createCampaign(payload: CampaignPayload) {
  creating.value = true
  createError.value = ''
  try {
    const campaign = await store.createCampaign(payload)
    showCreate.value = false
    // Land on the composer so the user can review the audience and send.
    router.push({
      name: 'marketing-campaign-detail',
      params: { projectName: String(route.params.projectName), campaignId: campaign.id },
    })
  } catch (error) {
    createError.value = extractError(error, 'Could not create the campaign.')
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  await load()
  // Tags power the audience picker in the create form.
  try {
    await store.fetchTags()
  } catch {
    // Non-fatal: the form falls back to "all contacts".
  }
})
</script>
