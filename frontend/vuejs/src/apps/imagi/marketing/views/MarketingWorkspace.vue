<!--
  MarketingWorkspace.vue - Shell for the per-project marketing workspace.

  Resolves the project from the URL slug (like ProjectHub), points the
  marketing store at it, and renders the tab navigation with a child
  router-view for Campaigns / Audience / Inbox / Channels.

  Route: /imagi/project/:projectName/marketing
-->
<template>
  <ToolWorkspaceShell
    :project-name="projectName"
    :project="project"
    :is-loading="isLoading"
    title="Marketing"
    description="Run campaigns that reach your customers: texts to your contacts through Twilio, and search ads on Google."
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
  {
    name: 'marketing-overview',
    label: 'Campaigns',
    icon: 'fa-paper-plane',
    children: ['marketing-campaign-detail', 'marketing-ad-new', 'marketing-ad-draft', 'marketing-ads'],
  },
  { name: 'marketing-audience', label: 'Audience', icon: 'fa-address-book' },
  { name: 'marketing-inbox', label: 'Inbox', icon: 'fa-inbox' },
  { name: 'marketing-settings', label: 'Channels', icon: 'fa-plug' },
]

// Pages that already say which channels are connected don't need the banner.
const BANNERLESS = new Set(['marketing-settings', 'marketing-overview', 'marketing-ad-new', 'marketing-ad-draft', 'marketing-ads'])

const showConnectBanner = computed(() =>
  marketingStore.settings !== null
  && !marketingStore.isConfigured
  && !BANNERLESS.has(String(route.name))
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
