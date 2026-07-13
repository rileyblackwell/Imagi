<!--
  SellWorkspace.vue - Shell for the per-project sell workspace.

  Resolves the project from the URL slug (like ProjectHub), points the
  sell store at it, and renders the tab navigation with a child
  router-view for Overview / Products / Orders / Customers / Settings.

  Route: /imagi/project/:projectName/sales
-->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="bg-orange-50 dark:bg-[#16120e] relative transition-colors duration-500 min-h-screen overflow-hidden">
      <!-- Subtle background matching home page -->
      <div class="absolute inset-0 pointer-events-none">
        <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]"
             style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
      </div>

      <main class="relative z-10 flex flex-col px-6 sm:px-8 lg:px-12 pt-20 pb-16 min-h-screen">
        <div class="max-w-6xl mx-auto w-full">

          <!-- Back link -->
          <router-link
            :to="{ name: 'project-hub', params: { projectName } }"
            class="inline-flex items-center gap-2 text-sm font-medium text-blue-950/60 dark:text-blue-100/60 hover:text-blue-950 dark:hover:text-white transition-colors duration-200 mb-6"
          >
            <i class="fas fa-arrow-left text-xs"></i>
            <span>Project workspace</span>
          </router-link>

          <!-- Loading -->
          <div v-if="isLoading" class="flex flex-col items-center justify-center py-24">
            <div class="w-12 h-12 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.12] rounded-full flex items-center justify-center mb-4">
              <div class="w-6 h-6 border-2 border-emerald-200 dark:border-emerald-300/30 border-t-emerald-600 dark:border-t-emerald-300 rounded-full animate-spin"></div>
            </div>
            <p class="text-blue-950/70 dark:text-blue-100/70 text-sm transition-colors duration-300">Loading sell workspace...</p>
          </div>

          <!-- Not found -->
          <div v-else-if="!project" class="flex flex-col items-center justify-center py-24 text-center">
            <div class="w-16 h-16 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.12] rounded-full flex items-center justify-center mb-6">
              <i class="fas fa-folder-open text-2xl text-blue-950/40 dark:text-white/40"></i>
            </div>
            <h2 class="text-2xl font-semibold text-blue-950 dark:text-white mb-3 transition-colors duration-300">Project not found</h2>
            <p class="text-blue-950/70 dark:text-blue-100/70 mb-8 max-w-md transition-colors duration-300">We couldn't find this project. It may have been deleted.</p>
            <router-link :to="{ name: 'projects' }" :class="ui.secondaryBtn">
              <i class="fas fa-arrow-left text-sm"></i>
              <span>Back to projects</span>
            </router-link>
          </div>

          <template v-else>
            <!-- Header -->
            <section class="flex flex-col sm:flex-row sm:items-center gap-5 mb-6">
              <div class="w-16 h-16 text-2xl shrink-0" :class="ui.iconTile">
                <i class="fas fa-hand-holding-dollar"></i>
              </div>
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-3 mb-1.5">
                  <h1 class="text-3xl font-semibold text-blue-950 dark:text-white tracking-tight transition-colors duration-300">Sell</h1>
                  <span :class="ui.sectionBadge">{{ project.name }}</span>
                </div>
                <p class="text-base text-blue-950/70 dark:text-blue-100/70 max-w-2xl transition-colors duration-300">
                  Take payments for your business — products, checkout links, orders, and customers in one place, powered by Stripe.
                </p>
              </div>
            </section>

            <!-- Connect banner -->
            <div
              v-if="showConnectBanner"
              class="flex flex-col sm:flex-row sm:items-center gap-4 p-4 rounded-2xl border border-emerald-200/80 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-400/10 mb-6 transition-colors duration-300"
            >
              <div class="flex items-center gap-3 flex-1 min-w-0">
                <i class="fas fa-plug-circle-bolt text-emerald-600 dark:text-emerald-300"></i>
                <p class="text-sm text-emerald-900 dark:text-emerald-100">
                  Connect your Stripe account to start selling. You'll need your Stripe secret key — payments go straight to your own Stripe account.
                </p>
              </div>
              <router-link
                :to="{ name: 'sell-settings', params: { projectName } }"
                class="shrink-0"
                :class="ui.primaryBtn"
              >
                Connect Stripe
              </router-link>
            </div>

            <!-- Tabs -->
            <nav class="flex items-center gap-1.5 overflow-x-auto pb-px mb-6 border-b border-blue-200/60 dark:border-white/[0.1]">
              <router-link
                v-for="tab in tabs"
                :key="tab.name"
                :to="{ name: tab.name, params: { projectName } }"
                class="inline-flex items-center gap-2 px-4 py-2.5 rounded-t-xl text-sm font-medium whitespace-nowrap border-b-2 -mb-px transition-colors duration-200"
                :class="isActiveTab(tab)
                  ? 'border-emerald-500 dark:border-emerald-400 text-blue-950 dark:text-white'
                  : 'border-transparent text-blue-950/60 dark:text-blue-100/60 hover:text-blue-950 dark:hover:text-white'"
              >
                <i :class="['fas', tab.icon]" class="text-xs"></i>
                {{ tab.label }}
              </router-link>
            </nav>

            <!-- Active tab -->
            <router-view v-if="sellStore.projectId" />
          </template>
        </div>
      </main>
    </div>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { DefaultLayout } from '@/shared/layouts'
import { useAuthStore } from '@/shared/stores/auth'
import { useProjectStore } from '@/apps/imagi/build/stores/projectStore'
import { matchesSlug } from '@/apps/imagi/build/utils/slug'
import type { Project } from '@/apps/imagi/build/types/components'
import { useSellStore } from '../stores/sell'
import { ui } from '../utils/ui'

const props = defineProps<{
  projectName: string
}>()

const route = useRoute()
const authStore = useAuthStore()
const projectStore = useProjectStore()
const sellStore = useSellStore()

const isInitializing = ref(true)

const isLoading = computed(() => projectStore.loading || isInitializing.value)

const project = computed<Project | null>(() => {
  return projectStore.projects.find(p => matchesSlug(p.name, props.projectName)) || null
})

interface Tab { name: string; label: string; icon: string; children?: string[] }

const tabs: Tab[] = [
  { name: 'sell-overview', label: 'Overview', icon: 'fa-chart-line' },
  { name: 'sell-payments', label: 'Payments', icon: 'fa-credit-card' },
  { name: 'sell-products', label: 'Products', icon: 'fa-box-open' },
  { name: 'sell-orders', label: 'Orders', icon: 'fa-receipt' },
  { name: 'sell-customers', label: 'Customers', icon: 'fa-address-book' },
  { name: 'sell-settings', label: 'Settings', icon: 'fa-gear' },
]

function isActiveTab(tab: Tab): boolean {
  const current = String(route.name ?? '')
  return current === tab.name || Boolean(tab.children?.includes(current))
}

const showConnectBanner = computed(() =>
  sellStore.settings !== null
  && !sellStore.isConfigured
  && route.name !== 'sell-settings'
)

async function loadProject() {
  isInitializing.value = true
  try {
    if (!authStore.isAuthenticated) return
    if (projectStore.isAuthenticated !== authStore.isAuthenticated) {
      projectStore.setAuthenticated(authStore.isAuthenticated)
    }
    if (!projectStore.projects.length) {
      await projectStore.fetchProjects()
    }
  } catch (error) {
    console.error('Failed to load project for sell workspace:', error)
  } finally {
    isInitializing.value = false
  }
}

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

onMounted(loadProject)

watch(() => props.projectName, loadProject)
</script>

<!-- Unscoped so the crisp-card treatment reaches the tab views rendered in
     the child router-view. Matches the definition used on Home/hub cards. -->
<style>
.crisp-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.dark .crisp-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}
</style>
