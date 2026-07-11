<!--
  MarketingOverview.vue - Marketing dashboard: key stats for the last 30 days,
  recent campaigns, and the latest customer replies.
-->
<template>
  <div>
    <!-- Loading -->
    <div v-if="store.overviewLoading && !overview" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-violet-200 dark:border-violet-300/30 border-t-violet-600 dark:border-t-violet-300 rounded-full animate-spin"></div>
    </div>

    <template v-else-if="overview">
      <!-- Stats -->
      <section class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div v-for="stat in statCards" :key="stat.label" class="p-5" :class="ui.card">
          <div class="flex items-center gap-2 mb-2">
            <i :class="['fas', stat.icon]" class="text-xs text-violet-600 dark:text-violet-300"></i>
            <p class="text-xs font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-blue-100/50">{{ stat.label }}</p>
          </div>
          <p class="text-2xl font-semibold text-blue-950 dark:text-white tabular-nums">{{ stat.value }}</p>
          <p class="text-xs text-blue-950/50 dark:text-blue-100/50 mt-1">{{ stat.caption }}</p>
        </div>
      </section>

      <!-- Quick actions -->
      <section class="flex flex-wrap gap-3 mb-8">
        <router-link :to="{ name: 'marketing-campaigns', params: { projectName: route.params.projectName }, query: { new: '1' } }" :class="ui.primaryBtn">
          <i class="fas fa-paper-plane text-xs"></i>
          New campaign
        </router-link>
        <router-link :to="{ name: 'marketing-audience', params: { projectName: route.params.projectName } }" :class="ui.secondaryBtn">
          <i class="fas fa-user-plus text-xs"></i>
          Add contacts
        </router-link>
        <router-link :to="{ name: 'marketing-inbox', params: { projectName: route.params.projectName } }" :class="ui.secondaryBtn">
          <i class="fas fa-inbox text-xs"></i>
          Open inbox
        </router-link>
      </section>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Recent campaigns -->
        <section class="p-6" :class="ui.card">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-semibold text-blue-950 dark:text-white">Recent campaigns</h2>
            <router-link
              :to="{ name: 'marketing-campaigns', params: { projectName: route.params.projectName } }"
              class="text-sm font-medium text-violet-700 dark:text-violet-300 hover:text-violet-900 dark:hover:text-violet-200 transition-colors duration-200"
            >
              View all
            </router-link>
          </div>
          <div v-if="overview.recent_campaigns.length" class="space-y-3">
            <router-link
              v-for="campaign in overview.recent_campaigns"
              :key="campaign.id"
              :to="{ name: 'marketing-campaign-detail', params: { projectName: route.params.projectName, campaignId: campaign.id } }"
              class="flex items-center gap-3 p-3 rounded-xl border border-blue-200/60 dark:border-white/[0.08] hover:border-violet-200 dark:hover:border-violet-400/30 hover:bg-violet-50/50 dark:hover:bg-violet-400/[0.06] transition-all duration-200"
            >
              <div class="w-9 h-9 shrink-0" :class="ui.iconTile">
                <i :class="['fas', campaign.channel === 'voice' ? 'fa-phone-volume' : 'fa-comment-sms']" class="text-sm"></i>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-blue-950 dark:text-white truncate">{{ campaign.name }}</p>
                <p class="text-xs text-blue-950/50 dark:text-blue-100/50">
                  {{ campaign.stats.recipients }} recipient{{ campaign.stats.recipients === 1 ? '' : 's' }} · {{ formatDateTime(campaign.created_at) }}
                </p>
              </div>
              <StatusBadge :status="campaign.status" />
            </router-link>
          </div>
          <div v-else class="py-10 text-center">
            <p class="text-sm text-blue-950/60 dark:text-blue-100/60 mb-4">No campaigns yet. Send your first message to your audience.</p>
            <router-link :to="{ name: 'marketing-campaigns', params: { projectName: route.params.projectName }, query: { new: '1' } }" :class="ui.secondaryBtn">
              Create a campaign
            </router-link>
          </div>
        </section>

        <!-- Recent replies -->
        <section class="p-6" :class="ui.card">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-base font-semibold text-blue-950 dark:text-white">Latest replies</h2>
            <router-link
              :to="{ name: 'marketing-inbox', params: { projectName: route.params.projectName } }"
              class="text-sm font-medium text-violet-700 dark:text-violet-300 hover:text-violet-900 dark:hover:text-violet-200 transition-colors duration-200"
            >
              Open inbox
            </router-link>
          </div>
          <div v-if="overview.recent_inbound.length" class="space-y-3">
            <div
              v-for="message in overview.recent_inbound"
              :key="message.id"
              class="flex items-start gap-3 p-3 rounded-xl border border-blue-200/60 dark:border-white/[0.08]"
            >
              <div class="w-9 h-9 shrink-0 rounded-xl flex items-center justify-center border bg-blue-50 dark:bg-blue-400/10 border-blue-200/60 dark:border-blue-400/25 text-blue-600 dark:text-blue-300">
                <i class="fas fa-reply text-sm"></i>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between gap-2">
                  <p class="text-sm font-medium text-blue-950 dark:text-white truncate">{{ message.contact_name }}</p>
                  <p class="text-xs text-blue-950/50 dark:text-blue-100/50 whitespace-nowrap">{{ formatDateTime(message.created_at) }}</p>
                </div>
                <p class="text-sm text-blue-950/70 dark:text-blue-100/70 truncate">{{ message.body || '(no text)' }}</p>
              </div>
            </div>
          </div>
          <div v-else class="py-10 text-center">
            <p class="text-sm text-blue-950/60 dark:text-blue-100/60">
              No replies yet. When customers text your Twilio number, their messages land here and in the inbox.
            </p>
          </div>
        </section>
      </div>
    </template>

    <div v-else-if="loadError" :class="ui.errorBox">{{ loadError }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import StatusBadge from '../components/StatusBadge.vue'
import { extractError } from '../services/marketingService'
import { useMarketingStore } from '../stores/marketing'
import { formatDateTime, ui } from '../utils/ui'

const route = useRoute()
const store = useMarketingStore()
const loadError = ref('')

const overview = computed(() => store.overview)

const statCards = computed(() => {
  const stats = overview.value?.stats
  if (!stats) return []
  const deliveryRate = stats.messages_sent_30d
    ? Math.round((stats.messages_delivered_30d / stats.messages_sent_30d) * 100)
    : null
  return [
    {
      label: 'Audience',
      icon: 'fa-address-book',
      value: stats.contacts_total.toLocaleString(),
      caption: `${stats.contacts_subscribed.toLocaleString()} subscribed`,
    },
    {
      label: 'Messages sent',
      icon: 'fa-paper-plane',
      value: stats.messages_sent_30d.toLocaleString(),
      caption: 'last 30 days',
    },
    {
      label: 'Delivered',
      icon: 'fa-circle-check',
      value: stats.messages_delivered_30d.toLocaleString(),
      caption: deliveryRate === null ? 'last 30 days' : `${deliveryRate}% delivery rate`,
    },
    {
      label: 'Replies',
      icon: 'fa-reply',
      value: stats.replies_30d.toLocaleString(),
      caption: `${stats.campaigns_active} active campaign${stats.campaigns_active === 1 ? '' : 's'}`,
    },
  ]
})

onMounted(async () => {
  try {
    await store.fetchOverview()
  } catch (error) {
    loadError.value = extractError(error, 'Could not load the marketing overview.')
  }
})
</script>
