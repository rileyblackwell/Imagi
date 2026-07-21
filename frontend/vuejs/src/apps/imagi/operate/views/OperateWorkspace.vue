<!--
  OperateWorkspace.vue - Shell for the per-project Operate workspace, the
  central hub for running the business.

  Resolves the project from the URL slug (like ProjectHub), points the
  operate store at it, and renders the tab navigation with a child
  router-view for Dashboard / Finance / Invoices / Tasks.

  Route: /imagi/project/:projectName/operations
-->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="relative min-h-screen overflow-hidden bg-[linear-gradient(180deg,#fdf9f2_0%,#faf7f1_60%,#ffffff_100%)] dark:bg-[linear-gradient(180deg,#0c0c0e_0%,#0a0b0f_60%,#0a0a0a_100%)] transition-colors duration-500">
      <main class="relative z-10 flex flex-col px-6 sm:px-8 lg:px-12 pt-20 pb-16 min-h-screen">
        <div class="max-w-6xl mx-auto w-full">

          <!-- Back link -->
          <router-link
            :to="{ name: 'project-hub', params: { projectName } }"
            class="inline-flex items-center gap-2 rounded-md text-sm font-medium text-blue-950/60 dark:text-blue-100/60 hover:text-blue-950 dark:hover:text-white transition-colors duration-200 mb-6 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
          >
            <i class="fas fa-arrow-left text-xs"></i>
            <span>Project workspace</span>
          </router-link>

          <!-- Loading -->
          <div v-if="isLoading" class="flex flex-col items-center justify-center py-24">
            <div class="w-12 h-12 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.12] rounded-full flex items-center justify-center mb-4">
              <div class="w-6 h-6 border-2 border-blue-200 dark:border-blue-300/30 border-t-blue-600 dark:border-t-blue-300 rounded-full animate-spin"></div>
            </div>
            <p class="text-blue-950/70 dark:text-blue-100/70 text-sm transition-colors duration-300">Loading operate workspace...</p>
          </div>

          <!-- Not found -->
          <div v-else-if="!project" class="flex flex-col items-center justify-center py-24 text-center">
            <div class="w-16 h-16 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.12] rounded-full flex items-center justify-center mb-6">
              <i class="fas fa-folder-open text-2xl text-blue-950/40 dark:text-blue-100/40"></i>
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
                <i class="fas fa-briefcase"></i>
              </div>
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-3 mb-1.5">
                  <h1 class="font-display text-3xl font-semibold text-blue-950 dark:text-white tracking-[-0.02em] leading-[1.05] transition-colors duration-300">Operate</h1>
                  <span :class="ui.sectionBadge">{{ project.name }}</span>
                </div>
                <p class="text-base text-blue-950/70 dark:text-blue-100/70 max-w-2xl transition-colors duration-300">
                  The central hub for running your business — money in and out, invoices, and the day-to-day work, all in one place.
                </p>
              </div>
            </section>

            <!-- Tabs -->
            <nav class="flex items-center gap-1.5 overflow-x-auto pb-px mb-6 border-b border-blue-200/60 dark:border-white/[0.1]">
              <router-link
                v-for="tab in tabs"
                :key="tab.name"
                :to="{ name: tab.name, params: { projectName } }"
                class="inline-flex items-center gap-2 px-4 py-2.5 rounded-t-xl text-sm font-medium whitespace-nowrap border-b-2 -mb-px transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-inset"
                :class="route.name === tab.name
                  ? 'border-orange-500 dark:border-orange-400 text-blue-950 dark:text-white'
                  : 'border-transparent text-blue-950/60 dark:text-blue-100/60 hover:text-blue-950 dark:hover:text-white'"
              >
                <i :class="['fas', tab.icon]" class="text-xs"></i>
                {{ tab.label }}
              </router-link>
            </nav>

            <!-- Active tab -->
            <router-view v-if="operateStore.projectId" />
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
import { useOperateStore } from '../stores/operate'
import { ui } from '../utils/ui'

const props = defineProps<{
  projectName: string
}>()

const route = useRoute()
const authStore = useAuthStore()
const projectStore = useProjectStore()
const operateStore = useOperateStore()

const isInitializing = ref(true)

const isLoading = computed(() => projectStore.loading || isInitializing.value)

const project = computed<Project | null>(() => {
  return projectStore.projects.find(p => matchesSlug(p.name, props.projectName)) || null
})

interface Tab { name: string; label: string; icon: string }

const tabs: Tab[] = [
  { name: 'operate-dashboard', label: 'Dashboard', icon: 'fa-gauge-high' },
  { name: 'operate-finance', label: 'Finance', icon: 'fa-file-invoice-dollar' },
  { name: 'operate-invoices', label: 'Invoices', icon: 'fa-receipt' },
  { name: 'operate-tasks', label: 'Tasks', icon: 'fa-list-check' },
]

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
    console.error('Failed to load project for operate workspace:', error)
  } finally {
    isInitializing.value = false
  }
}

// Point the operate store at the resolved project so tab views can load data.
watch(project, (resolved) => {
  if (resolved?.id != null) {
    operateStore.setProject(Number(resolved.id))
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
