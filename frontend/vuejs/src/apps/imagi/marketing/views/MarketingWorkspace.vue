<!--
  MarketingWorkspace.vue - Shell for the per-project marketing workspace.

  Resolves the project from the URL slug (like ProjectHub), points the
  marketing store at it, and renders the tab navigation with a child
  router-view for Overview / Campaigns / Audience / Inbox / Settings.

  Route: /imagi/project/:projectName/marketing
-->
<template>
  <ToolWorkspaceShell
    :project-name="projectName"
    :project="project"
    :is-loading="isLoading"
    title="Marketing"
    description="Reach customers and drive sales — text and voice campaigns powered by Twilio, plus your Google and Meta ad campaigns, all in one place."
    loading-label="Loading marketing workspace…"
    :tabs="tabs"
    :show-banner="showConnectBanner"
  >
    <template #banner>
      Connect your Twilio account to start sending. You'll need your Account SID, auth token, and a Twilio phone number.
    </template>
    <template #banner-action>
      <router-link :to="{ name: 'marketing-settings', params: { projectName } }" :class="ui.primaryBtn">
        Connect Twilio
      </router-link>
    </template>

    <router-view v-if="marketingStore.projectId" />
  </ToolWorkspaceShell>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectFromSlug, ToolWorkspaceShell, type ToolTab } from '@/apps/imagi/shared'
import { useMarketingStore } from '../stores/marketing'
import { ui } from '../utils/ui'

const props = defineProps<{
  projectName: string
}>()

const route = useRoute()

const { project, isLoading } = useProjectFromSlug(() => props.projectName, 'the marketing workspace')
const marketingStore = useMarketingStore()

const tabs: ToolTab[] = [
  { name: 'marketing-overview', label: 'Overview', icon: 'fa-chart-line' },
  { name: 'marketing-campaigns', label: 'Campaigns', icon: 'fa-paper-plane', children: ['marketing-campaign-detail'] },
  { name: 'marketing-audience', label: 'Audience', icon: 'fa-address-book' },
  { name: 'marketing-ads', label: 'Ads', icon: 'fa-rectangle-ad' },
  { name: 'marketing-inbox', label: 'Inbox', icon: 'fa-inbox' },
  { name: 'marketing-settings', label: 'Settings', icon: 'fa-gear' },
]

const showConnectBanner = computed(() =>
  marketingStore.settings !== null
  && !marketingStore.isConfigured
  && route.name !== 'marketing-settings'
)

// Point the marketing store at the resolved project and load settings once
// (they drive the connect banner and the Settings tab).
watch(project, async (resolved) => {
  if (resolved?.id != null) {
    marketingStore.setProject(Number(resolved.id))
    if (!marketingStore.settings) {
      try {
        await marketingStore.fetchSettings()
      } catch (error) {
        console.error('Failed to load marketing settings:', error)
      }
    }
  }
}, { immediate: true })

</script>
