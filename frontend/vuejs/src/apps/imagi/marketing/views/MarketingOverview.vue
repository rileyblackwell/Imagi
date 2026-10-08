<!--
  MarketingOverview.vue - The Campaigns home, and Market's landing page.

  Market is a place to run campaigns, so this page leads with the two ways to
  start one: a text message to your contacts (Twilio) and a Google search ad.
  Each channel card says whether its account is connected. Under them sit the
  month's numbers and one list of every campaign across both channels: text
  campaigns, Google ads planned in Imagi, and campaigns synced from a
  connected ad account.
-->
<template>
  <div>
    <!-- Start a campaign -->
    <section aria-labelledby="start-heading">
      <h2 id="start-heading" :class="ui.label" class="mb-4">Start a campaign</h2>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <ChannelCard
          title="Text message"
          via="Sent through your Twilio account"
          icon="fas fa-comment-sms"
          :connected="twilioConnected"
          description="Text your contacts about a launch, an offer or a reminder. Replies come back to your inbox, and anyone who texts STOP is taken off the list."
          :detail="textDetail"
        >
          <template #actions>
            <button type="button" :class="ui.secondaryBtn" @click="showCreate = true">
              Write a text
            </button>
            <router-link
              v-if="!twilioConnected"
              :to="{ name: 'marketing-settings', params: { projectName } }"
              :class="ui.textLink"
            >
              Connect Twilio
            </router-link>
          </template>
        </ChannelCard>

        <ChannelCard
          title="Google search ad"
          via="Runs on your Google Ads account"
          icon="fab fa-google"
          :connected="googleConnected"
          description="Show up when people search for what you sell. You pick the words, write the ad and set a daily budget, and Google charges only when someone clicks."
          :detail="adDetail"
        >
          <template #actions>
            <router-link :to="{ name: 'marketing-ad-new', params: { projectName } }" :class="ui.secondaryBtn">
              Plan an ad
            </router-link>
            <router-link
              v-if="googleConnected"
              :to="{ name: 'marketing-ads', params: { projectName } }"
              :class="ui.textLink"
            >
              See ad results
            </router-link>
            <router-link
              v-else
              :to="{ name: 'marketing-settings', params: { projectName } }"
              :class="ui.textLink"
            >
              Connect Google Ads
            </router-link>
          </template>
        </ChannelCard>
      </div>
    </section>

    <!-- This month -->
    <section v-if="stats" class="mt-10 grid grid-cols-2 lg:grid-cols-4 gap-4" aria-label="Last 30 days">
      <div v-for="stat in statCards" :key="stat.label" class="p-5" :class="ui.card">
        <p :class="ui.label" class="!mb-2">{{ stat.label }}</p>
        <p class="stat-number text-2xl font-semibold tabular-nums">{{ stat.value }}</p>
        <p :class="ui.hintText" class="mt-1">{{ stat.caption }}</p>
      </div>
    </section>

    <!-- Every campaign -->
    <section class="mt-12" aria-labelledby="campaigns-heading">
      <div class="flex flex-col sm:flex-row sm:items-center gap-3 mb-5">
        <h2 id="campaigns-heading" :class="ui.headingText" class="flex-1">Your campaigns</h2>
        <div class="flex items-center gap-1.5 flex-wrap" role="group" aria-label="Filter by channel">
          <button
            v-for="option in channelFilters"
            :key="option.value"
            type="button"
            class="px-3.5 py-1.5 rounded-full border text-xs font-semibold transition-all duration-200 focus-ring"
            :class="channelFilter === option.value ? ui.chipOn : ui.chipOff"
            :aria-pressed="channelFilter === option.value"
            @click="channelFilter = option.value"
          >
            {{ option.label }}
            <span class="ml-1 tabular-nums opacity-60">{{ countFor(option.value) }}</span>
          </button>
        </div>
      </div>

      <LoadingSpinner v-if="loading && !rows.length" />

      <div v-else-if="visibleRows.length" :class="ui.card" class="overflow-hidden">
        <component
          :is="row.to ? 'router-link' : 'div'"
          v-for="row in visibleRows"
          :key="row.key"
          :to="row.to"
          class="row group flex items-center gap-4 px-5 py-4 border-b border-[color:var(--sl-line)] last:border-b-0 focus-ring"
          :class="row.to ? 'hover:bg-ink/[0.025] dark:hover:bg-white/[0.03] transition-colors duration-200' : ''"
        >
          <div class="w-10 h-10 shrink-0" :class="ui.iconTile">
            <i :class="row.icon" aria-hidden="true"></i>
          </div>
          <div class="flex-1 min-w-0">
            <p :class="ui.panelHeading" class="truncate">{{ row.name }}</p>
            <p :class="ui.hintText" class="truncate mt-0.5">
              <span class="font-medium text-ink/70 dark:text-bone/70">{{ row.channel }}</span>
              <span v-if="row.sub"> · {{ row.sub }}</span>
            </p>
          </div>
          <div v-if="row.metric" class="text-right hidden sm:block">
            <p class="text-sm font-semibold text-ink dark:text-bone tabular-nums">{{ row.metric }}</p>
            <p :class="ui.hintText">{{ row.metricLabel }}</p>
          </div>
          <div class="text-right hidden md:block w-36">
            <p class="text-sm text-ink/70 dark:text-bone/70">{{ formatDateTime(row.when) }}</p>
            <p :class="ui.hintText">{{ row.whenLabel }}</p>
          </div>
          <StatusBadge :status="row.status" />
          <i
            class="fas fa-chevron-right text-xs text-ink/30 dark:text-bone/30 transition-transform duration-200 group-hover:translate-x-0.5"
            :class="{ invisible: !row.to }"
            aria-hidden="true"
          ></i>
        </component>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-16 text-center" :class="ui.card">
        <p :class="ui.panelHeading">{{ emptyTitle }}</p>
        <p :class="ui.bodyText" class="max-w-md mt-2">
          Start one above. Texts and Google ads you plan here show up in this list, with how each one is doing.
        </p>
      </div>

      <div v-if="loadError" class="mt-4" :class="ui.errorBox">{{ loadError }}</div>
    </section>

    <!-- New text campaign -->
    <BaseModal v-if="showCreate" title="New text campaign" wide @close="closeCreate">
      <CampaignForm
        :tags="store.tags"
        :busy="creating"
        :error="createError"
        submit-label="Save draft"
        @submit="createCampaign"
        @cancel="closeCreate"
      />
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter, type RouteLocationRaw } from 'vue-router'
import { BaseModal, LoadingSpinner } from '@/shared/components'
import CampaignForm from '../components/CampaignForm.vue'
import ChannelCard from '../components/ChannelCard.vue'
import StatusBadge from '../components/StatusBadge.vue'
import { extractError } from '../services/marketingService'
import { useMarketingStore } from '../stores/marketing'
import type { CampaignPayload } from '../types'
import { AD_PROVIDERS, formatCompactNumber, formatCurrency, formatDateTime, ui } from '../utils/ui'

type ChannelFilter = 'all' | 'text' | 'ads'

interface CampaignRow {
  key: string
  kind: 'text' | 'ads'
  name: string
  channel: string
  sub: string
  icon: string
  status: string
  metric: string
  metricLabel: string
  when: string
  whenLabel: string
  to: RouteLocationRaw | null
}

const route = useRoute()
const router = useRouter()
const store = useMarketingStore()

const projectName = computed(() => String(route.params.projectName))

const loading = ref(true)
const loadError = ref('')
const channelFilter = ref<ChannelFilter>('all')
const showCreate = ref(route.query.new === '1')
const creating = ref(false)
const createError = ref('')

const stats = computed(() => store.overview?.stats ?? null)
const twilioConnected = computed(() => store.isConfigured)
const googleConnected = computed(() =>
  store.adConnections.some(c => c.provider === 'google' && c.is_configured)
)

const textDetail = computed(() => {
  if (!stats.value) return ''
  const reach = stats.value.contacts_subscribed
  return reach
    ? `${reach.toLocaleString()} subscribed contact${reach === 1 ? '' : 's'} can get your next text.`
    : 'Add contacts in Audience before you send.'
})

const adDetail = computed(() => {
  const planned = store.adDrafts.length
  const live = store.adCampaigns.filter(c => c.provider === 'google').length
  const parts = []
  if (planned) parts.push(`${planned} planned in Imagi`)
  if (live) parts.push(`${live} on Google Ads`)
  return parts.length ? parts.join(' · ') : 'Plan an ad here now, and launch it once Google Ads is connected.'
})

const statCards = computed(() => {
  const s = stats.value
  if (!s) return []
  const summary = store.adsSummary
  const hasAds = Boolean(summary?.connected_providers.length)
  return [
    {
      label: 'Contacts',
      value: s.contacts_total.toLocaleString(),
      caption: `${s.contacts_subscribed.toLocaleString()} subscribed`,
    },
    {
      label: 'Texts delivered',
      value: s.messages_delivered_30d.toLocaleString(),
      caption: s.messages_sent_30d
        ? `${Math.round((s.messages_delivered_30d / s.messages_sent_30d) * 100)}% of ${s.messages_sent_30d.toLocaleString()} sent`
        : 'last 30 days',
    },
    {
      label: 'Replies',
      value: s.replies_30d.toLocaleString(),
      caption: 'last 30 days',
    },
    {
      label: 'Ad clicks',
      value: hasAds ? formatCompactNumber(summary!.clicks) : '—',
      caption: hasAds ? `${formatCurrency(summary!.spend, summary!.currency)} spent` : 'no ad account connected',
    },
  ]
})

const rows = computed<CampaignRow[]>(() => {
  const name = projectName.value
  const text: CampaignRow[] = store.campaigns.map(c => ({
    key: `text-${c.id}`,
    kind: 'text',
    name: c.name,
    channel: c.channel === 'voice' ? 'Voice call' : 'Text message',
    sub: c.body,
    icon: c.channel === 'voice' ? 'fas fa-phone-volume' : 'fas fa-comment-sms',
    status: c.status,
    metric: c.status === 'draft' ? '' : `${c.stats.delivered}/${c.stats.recipients}`,
    metricLabel: 'delivered',
    when: c.scheduled_at || c.updated_at || c.created_at,
    whenLabel: c.scheduled_at ? 'scheduled for' : 'updated',
    to: { name: 'marketing-campaign-detail', params: { projectName: name, campaignId: c.id } },
  }))

  const drafts: CampaignRow[] = store.adDrafts.map(d => ({
    key: `draft-${d.id}`,
    kind: 'ads',
    name: d.name,
    channel: 'Google search ad',
    sub: d.headlines[0] || 'No headline yet',
    icon: 'fab fa-google',
    status: 'draft',
    metric: d.daily_budget ? formatCurrency(d.daily_budget, 'USD') : '',
    metricLabel: 'a day',
    when: d.updated_at,
    whenLabel: 'updated',
    to: { name: 'marketing-ad-draft', params: { projectName: name, draftId: d.id } },
  }))

  const synced: CampaignRow[] = store.adCampaigns.map(a => ({
    key: `ad-${a.id}`,
    kind: 'ads',
    name: a.name,
    channel: AD_PROVIDERS[a.provider].label,
    sub: `${formatCompactNumber(a.clicks)} clicks · ${formatCurrency(a.spend, a.currency)} spent`,
    icon: AD_PROVIDERS[a.provider].icon,
    status: a.status === 'other' ? (a.provider_status || 'other').toLowerCase() : a.status,
    metric: a.ctr === null ? '' : `${a.ctr}%`,
    metricLabel: 'click rate',
    when: a.last_synced_at || '',
    whenLabel: 'synced',
    to: { name: 'marketing-ads', params: { projectName: name } },
  }))

  return [...text, ...drafts, ...synced].sort((a, b) => (b.when || '').localeCompare(a.when || ''))
})

const visibleRows = computed(() =>
  channelFilter.value === 'all' ? rows.value : rows.value.filter(r => r.kind === channelFilter.value)
)

const channelFilters: { value: ChannelFilter; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'text', label: 'Texts' },
  { value: 'ads', label: 'Ads' },
]

function countFor(filter: ChannelFilter) {
  return filter === 'all' ? rows.value.length : rows.value.filter(r => r.kind === filter).length
}

const emptyTitle = computed(() => ({
  all: 'No campaigns yet',
  text: 'No text campaigns yet',
  ads: 'No ads yet',
}[channelFilter.value]))

function closeCreate() {
  showCreate.value = false
  createError.value = ''
  if (route.query.new) router.replace({ query: {} })
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
      params: { projectName: projectName.value, campaignId: campaign.id },
    })
  } catch (error) {
    createError.value = extractError(error, 'Could not create the campaign.')
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  // Each source fails on its own: a missing ad account shouldn't hide texts.
  const results = await Promise.allSettled([
    store.fetchOverview(),
    store.fetchCampaigns(),
    store.fetchAdDrafts(),
    store.fetchAdConnections(),
    store.fetchAdCampaigns(),
    store.fetchTags(),
  ])
  const failed = results.slice(0, 3).find(r => r.status === 'rejected') as PromiseRejectedResult | undefined
  if (failed) loadError.value = extractError(failed.reason, 'Could not load your campaigns.')
  loading.value = false
})
</script>

<style scoped>
/* Stat numerals carry the light, as the design system asks. */
.stat-number {
  background: var(--sl-grad);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
</style>
