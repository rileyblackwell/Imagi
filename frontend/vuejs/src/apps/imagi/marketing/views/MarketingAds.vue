<!--
  MarketingAds.vue - Unified ads dashboard across Google Ads and Meta Ads:
  lifetime performance tiles, per-campaign table with pause/resume, and a
  sync action that refreshes everything from the platforms.

  Campaigns are created in the platforms' own managers (deep-linked from each
  row); Imagi mirrors them for one place to watch spend and results.
-->
<template>
  <div>
    <!-- Loading -->
    <div v-if="initialLoading" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-blue-200 dark:border-blue-300/30 border-t-blue-700 dark:border-t-blue-300 rounded-full animate-spin motion-reduce:animate-none"></div>
    </div>

    <!-- Nothing connected yet -->
    <div v-else-if="!hasConnections" class="p-10 text-center" :class="ui.card">
      <div class="w-16 h-16 mx-auto text-2xl mb-5" :class="ui.iconTile">
        <i class="fas fa-rectangle-ad"></i>
      </div>
      <h2 class="text-xl font-semibold text-blue-950 dark:text-white mb-2">Bring your ad campaigns into Imagi</h2>
      <p class="text-sm text-blue-950/60 dark:text-blue-100/60 max-w-lg mx-auto mb-7">
        Connect your Google Ads or Meta Ads account to see every campaign, its spend, and its
        results in one dashboard — and pause or resume campaigns without leaving Imagi.
      </p>
      <div class="flex flex-wrap items-center justify-center gap-3">
        <router-link :to="{ name: 'marketing-settings', params: { projectName: route.params.projectName } }" :class="ui.primaryBtn">
          <i class="fas fa-plug-circle-bolt text-xs"></i>
          Connect ad accounts
        </router-link>
      </div>
      <div class="flex items-center justify-center gap-6 mt-7 text-blue-950/40 dark:text-blue-100/40">
        <span class="inline-flex items-center gap-2 text-sm"><i class="fab fa-google"></i> Google Ads</span>
        <span class="inline-flex items-center gap-2 text-sm"><i class="fab fa-meta"></i> Meta Ads</span>
      </div>
    </div>

    <template v-else>
      <!-- Summary tiles -->
      <section v-if="summary" class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div v-for="stat in statCards" :key="stat.label" class="p-5" :class="ui.card">
          <div class="flex items-center gap-2 mb-2">
            <i :class="['fas', stat.icon]" class="text-xs text-blue-700 dark:text-blue-300"></i>
            <p class="text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50">{{ stat.label }}</p>
          </div>
          <p class="text-2xl font-semibold text-blue-950 dark:text-white tabular-nums">{{ stat.value }}</p>
          <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1">{{ stat.caption }}</p>
        </div>
      </section>

      <!-- Toolbar: provider filter + sync -->
      <section class="flex flex-wrap items-center gap-3 mb-6">
        <div class="flex items-center gap-1.5">
          <button
            v-for="option in providerFilters"
            :key="option.value"
            type="button"
            class="px-3.5 py-2 rounded-full text-sm font-medium border transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
            :class="providerFilter === option.value
              ? 'border-blue-300/80 dark:border-blue-400/40 bg-blue-100/80 dark:bg-blue-400/20 text-blue-900 dark:text-blue-200'
              : 'border-blue-200/70 dark:border-white/[0.12] bg-white dark:bg-white/[0.06] text-blue-950/70 dark:text-blue-100/70 hover:text-blue-950 dark:hover:text-white'"
            @click="setProviderFilter(option.value)"
          >
            <i v-if="option.icon" :class="option.icon" class="text-xs mr-1.5"></i>
            {{ option.label }}
          </button>
        </div>
        <div class="flex-1"></div>
        <p v-if="summary?.last_synced_at" class="text-xs text-blue-950/50 dark:text-blue-100/50">
          Synced {{ formatDateTime(summary.last_synced_at) }}
        </p>
        <button type="button" :class="ui.secondaryBtn" :disabled="store.adsSyncing" @click="sync">
          <i :class="['fas', store.adsSyncing ? 'fa-circle-notch animate-spin motion-reduce:animate-none' : 'fa-rotate']" class="text-xs"></i>
          {{ store.adsSyncing ? 'Syncing…' : 'Sync now' }}
        </button>
      </section>

      <div v-if="pageError" class="mb-6" :class="ui.errorBox">{{ pageError }}</div>
      <div v-if="syncNotice" class="mb-6" :class="ui.successBox">{{ syncNotice }}</div>

      <!-- Campaign table -->
      <section :class="ui.card">
        <div v-if="store.adCampaignsLoading && !campaigns.length" class="flex justify-center py-16">
          <div class="w-6 h-6 border-2 border-blue-200 dark:border-blue-300/30 border-t-blue-700 dark:border-t-blue-300 rounded-full animate-spin motion-reduce:animate-none"></div>
        </div>

        <div v-else-if="campaigns.length" class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-blue-200/60 dark:border-white/[0.08] text-left">
                <th class="px-5 py-3.5 text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50">Campaign</th>
                <th class="px-4 py-3.5 text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50">Status</th>
                <th class="px-4 py-3.5 text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50 text-right">Budget/day</th>
                <th class="px-4 py-3.5 text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50 text-right">Impressions</th>
                <th class="px-4 py-3.5 text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50 text-right">Clicks</th>
                <th class="px-4 py-3.5 text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50 text-right">CTR</th>
                <th class="px-4 py-3.5 text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50 text-right">Spend</th>
                <th class="px-4 py-3.5 text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50 text-right">CPC</th>
                <th class="px-4 py-3.5 text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50 text-right">Conv.</th>
                <th class="px-5 py-3.5"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="campaign in campaigns"
                :key="campaign.id"
                class="border-b border-blue-200/40 dark:border-white/[0.05] last:border-0 hover:bg-blue-50/40 dark:hover:bg-white/[0.03] transition-colors duration-150"
              >
                <td class="px-5 py-3.5">
                  <div class="flex items-center gap-3 min-w-0">
                    <i :class="AD_PROVIDERS[campaign.provider].icon" class="text-blue-950/50 dark:text-blue-100/50 shrink-0" :title="AD_PROVIDERS[campaign.provider].label"></i>
                    <div class="min-w-0">
                      <p class="font-medium text-blue-950 dark:text-white truncate max-w-56" :title="campaign.name">{{ campaign.name }}</p>
                      <p v-if="campaign.objective" class="text-xs text-blue-950/50 dark:text-blue-100/50 truncate">{{ formatObjective(campaign.objective) }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3.5"><StatusBadge :status="campaign.status" /></td>
                <td class="px-4 py-3.5 text-right tabular-nums text-blue-950/80 dark:text-blue-100/80">{{ formatCurrency(campaign.daily_budget, campaign.currency) }}</td>
                <td class="px-4 py-3.5 text-right tabular-nums text-blue-950/80 dark:text-blue-100/80">{{ formatCompactNumber(campaign.impressions) }}</td>
                <td class="px-4 py-3.5 text-right tabular-nums text-blue-950/80 dark:text-blue-100/80">{{ formatCompactNumber(campaign.clicks) }}</td>
                <td class="px-4 py-3.5 text-right tabular-nums text-blue-950/80 dark:text-blue-100/80">{{ campaign.ctr === null ? '—' : `${campaign.ctr}%` }}</td>
                <td class="px-4 py-3.5 text-right tabular-nums font-medium text-blue-950 dark:text-white">{{ formatCurrency(campaign.spend, campaign.currency) }}</td>
                <td class="px-4 py-3.5 text-right tabular-nums text-blue-950/80 dark:text-blue-100/80">{{ formatCurrency(campaign.cpc, campaign.currency) }}</td>
                <td class="px-4 py-3.5 text-right tabular-nums text-blue-950/80 dark:text-blue-100/80">{{ campaign.conversions === null ? '—' : formatCompactNumber(parseFloat(campaign.conversions)) }}</td>
                <td class="px-5 py-3.5">
                  <div class="flex items-center justify-end gap-1.5">
                    <button
                      v-if="campaign.status === 'active' || campaign.status === 'paused'"
                      type="button"
                      class="w-8 h-8 rounded-lg flex items-center justify-center text-blue-950/50 dark:text-blue-100/50 hover:text-blue-950 dark:hover:text-white hover:bg-blue-50 dark:hover:bg-white/[0.08] transition-colors duration-150 disabled:opacity-40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0c0c0e]"
                      :title="campaign.status === 'active' ? 'Pause campaign' : 'Resume campaign'"
                      :disabled="togglingId === campaign.id"
                      @click="toggle(campaign)"
                    >
                      <i :class="['fas', togglingId === campaign.id ? 'fa-circle-notch animate-spin motion-reduce:animate-none' : campaign.status === 'active' ? 'fa-pause' : 'fa-play']" class="text-xs"></i>
                    </button>
                    <a
                      :href="campaign.manager_url"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="w-8 h-8 rounded-lg flex items-center justify-center text-blue-950/50 dark:text-blue-100/50 hover:text-blue-950 dark:hover:text-white hover:bg-blue-50 dark:hover:bg-white/[0.08] transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0c0c0e]"
                      :title="`Open in ${AD_PROVIDERS[campaign.provider].consoleLabel}`"
                    >
                      <i class="fas fa-arrow-up-right-from-square text-xs"></i>
                    </a>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="py-14 text-center px-6">
          <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-5">
            {{ providerFilter
              ? `No ${AD_PROVIDERS[providerFilter].label} campaigns synced yet.`
              : 'No campaigns synced yet. Pull them in from your connected ad accounts.' }}
          </p>
          <button type="button" :class="ui.primaryBtn" :disabled="store.adsSyncing" @click="sync">
            <i :class="['fas', store.adsSyncing ? 'fa-circle-notch animate-spin motion-reduce:animate-none' : 'fa-rotate']" class="text-xs"></i>
            Sync campaigns
          </button>
        </div>
      </section>

      <!-- Where ads are created -->
      <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-4">
        New campaigns are created in
        <a href="https://ads.google.com" target="_blank" rel="noopener noreferrer" class="text-blue-700 dark:text-blue-300 hover:underline rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]">Google Ads</a>
        or
        <a href="https://adsmanager.facebook.com" target="_blank" rel="noopener noreferrer" class="text-blue-700 dark:text-blue-300 hover:underline rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]">Meta Ads Manager</a>
        — once live, they appear here on the next sync.
      </p>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import StatusBadge from '../components/StatusBadge.vue'
import { extractError } from '../services/marketingService'
import { useMarketingStore } from '../stores/marketing'
import type { AdCampaign, AdProvider } from '../types'
import { AD_PROVIDERS, formatCompactNumber, formatCurrency, formatDateTime, ui } from '../utils/ui'

const route = useRoute()
const store = useMarketingStore()

const initialLoading = ref(true)
const pageError = ref('')
const syncNotice = ref('')
const providerFilter = ref<AdProvider | ''>('')
const togglingId = ref<number | null>(null)

const summary = computed(() => store.adsSummary)
const campaigns = computed(() => store.adCampaigns)
const hasConnections = computed(() => store.hasAdsConnected)

const providerFilters = computed(() => [
  { value: '' as const, label: 'All platforms', icon: '' },
  ...store.adConnections
    .filter(c => c.is_configured)
    .map(c => ({
      value: c.provider,
      label: AD_PROVIDERS[c.provider].label,
      icon: AD_PROVIDERS[c.provider].icon,
    })),
])

const statCards = computed(() => {
  if (!summary.value) return []
  const s = summary.value
  const ctr = s.impressions ? `${(s.clicks / s.impressions * 100).toFixed(2)}% CTR` : 'no impressions yet'
  return [
    {
      label: 'Ad spend',
      icon: 'fa-coins',
      value: formatCurrency(s.spend, s.currency),
      caption: 'lifetime, all campaigns',
    },
    {
      label: 'Impressions',
      icon: 'fa-eye',
      value: formatCompactNumber(s.impressions),
      caption: 'times your ads were shown',
    },
    {
      label: 'Clicks',
      icon: 'fa-arrow-pointer',
      value: formatCompactNumber(s.clicks),
      caption: ctr,
    },
    {
      label: 'Campaigns',
      icon: 'fa-rectangle-ad',
      value: String(s.campaigns_total),
      caption: `${s.campaigns_active} active`,
    },
  ]
})

/** "OUTCOME_TRAFFIC" / "SEARCH" -> "Outcome traffic" / "Search". */
function formatObjective(value: string): string {
  const text = value.replace(/_/g, ' ').toLowerCase()
  return text.charAt(0).toUpperCase() + text.slice(1)
}

function setProviderFilter(value: AdProvider | '') {
  providerFilter.value = value
  refresh()
}

async function refresh() {
  pageError.value = ''
  try {
    await store.fetchAdCampaigns(providerFilter.value ? { provider: providerFilter.value } : {})
  } catch (error) {
    pageError.value = extractError(error, 'Could not load ad campaigns.')
  }
}

async function sync() {
  pageError.value = ''
  syncNotice.value = ''
  try {
    const result = await store.syncAds()
    const failed = Object.entries(result.errors)
    if (failed.length) {
      pageError.value = failed
        .map(([provider, message]) => `${AD_PROVIDERS[provider as AdProvider].label}: ${message}`)
        .join(' — ')
    }
    const synced = Object.values(result.results).reduce((sum, r) => sum + (r?.synced ?? 0), 0)
    if (!failed.length) {
      syncNotice.value = `Synced ${synced} campaign${synced === 1 ? '' : 's'} from your connected accounts.`
    }
    if (providerFilter.value) await refresh()
  } catch (error) {
    pageError.value = extractError(error, 'Could not sync your ad accounts.')
  }
}

async function toggle(campaign: AdCampaign) {
  togglingId.value = campaign.id
  pageError.value = ''
  try {
    await store.setAdCampaignStatus(campaign.id, campaign.status === 'active' ? 'pause' : 'resume')
  } catch (error) {
    pageError.value = extractError(error, 'Could not update the campaign.')
  } finally {
    togglingId.value = null
  }
}

onMounted(async () => {
  try {
    if (!store.adConnections.length) {
      await store.fetchAdConnections()
    }
    if (store.hasAdsConnected) {
      await refresh()
    }
  } catch (error) {
    pageError.value = extractError(error, 'Could not load the ads dashboard.')
  } finally {
    initialLoading.value = false
  }
})
</script>
