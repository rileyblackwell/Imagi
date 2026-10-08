<!--
  SellWorkspace.vue - Shell for the per-project sell workspace.

  Resolves the project from the URL slug (like ProjectHub), points the
  sell store at it, and renders the tab navigation with a child
  router-view for Console / Prices / Orders / Subscriptions / Customers /
  Settings.

  Route: /imagi/project/:projectName/sales
-->
<template>
  <ToolWorkspaceShell
    :project-name="projectName"
    :project="project"
    :is-loading="isLoading"
    title="Sell"
    description="Take payments in your app. Connect Stripe, choose how you charge, set your prices, and Imagi adds secure payment pages to your app."
    loading-label="Loading sell workspace…"
    :tabs="tabs"
    :show-banner="showConnectBanner"
  >
    <template #banner>
      Connect Stripe to start taking payments. Payments go straight to your own Stripe account.
    </template>
    <template #banner-action>
      <router-link :to="{ name: 'sell-overview', params: { projectName } }" :class="ui.primaryBtn">
        Connect Stripe
      </router-link>
    </template>

    <router-view v-if="sellStore.projectId" />
  </ToolWorkspaceShell>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectFromSlug, ToolWorkspaceShell, type ToolTab } from '@/apps/imagi/shared'
import { useSellStore } from '../stores/sell'
import { ui } from '../utils/ui'

const props = defineProps<{
  projectName: string
}>()

const route = useRoute()

const { project, isLoading } = useProjectFromSlug(() => props.projectName, 'the sell workspace')
const sellStore = useSellStore()

const tabs: ToolTab[] = [
  { name: 'sell-overview', label: 'Console', icon: 'fa-sliders' },
  { name: 'sell-products', label: 'Prices', icon: 'fa-tag' },
  { name: 'sell-orders', label: 'Orders', icon: 'fa-receipt' },
  { name: 'sell-subscriptions', label: 'Subscriptions', icon: 'fa-arrows-rotate' },
  { name: 'sell-customers', label: 'Customers', icon: 'fa-address-book' },
  { name: 'sell-settings', label: 'Settings', icon: 'fa-gear' },
]

const showConnectBanner = computed(() =>
  sellStore.settings !== null
  && !sellStore.isConfigured
  && route.name !== 'sell-settings'
  // The console's first step is connecting, so it needs no banner.
  && route.name !== 'sell-overview'
)

// Point the sell store at the resolved project and load settings once
// (they drive the connect banner and the Settings tab).
watch(project, async (resolved) => {
  if (resolved?.id != null) {
    sellStore.setProject(Number(resolved.id))
    if (!sellStore.settings) {
      try {
        await sellStore.fetchSettings()
      } catch (error) {
        console.error('Failed to load sell settings:', error)
      }
    }
  }
}, { immediate: true })

</script>
