<!--
  ProjectHub.vue - Project Overview / Workspace Hub

  This is the landing page for a single project (business). From here the user
  chooses how to work on it:
    - Build   -> the AI app builder (real, existing workspace)
    - Sell    -> sales tools (general template, coming soon)
    - Market  -> marketing tools (general template, coming soon)
    - Operate -> finance & operations tools (general template, coming soon)

  The categories are driven by utils/businessTools.ts. This view is a template
  shell — it does not implement any of the specific tools.
-->
<template>
  <DefaultLayout :isHomeNav="true">
    <div class="bg-orange-50 dark:bg-[#16120e] relative transition-colors duration-500 min-h-screen overflow-hidden">
      <!-- Subtle background matching home page -->
      <div class="absolute inset-0 pointer-events-none">
        <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]"
             style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
      </div>

      <main class="relative z-10 flex flex-col px-6 sm:px-8 lg:px-12 pt-20 pb-12 min-h-screen">
        <div class="max-w-6xl mx-auto w-full">

          <!-- Back link -->
          <router-link
            :to="{ name: 'projects' }"
            class="inline-flex items-center gap-2 text-sm font-medium text-blue-950/60 dark:text-blue-100/60 hover:text-blue-950 dark:hover:text-white transition-colors duration-200 mb-6"
          >
            <i class="fas fa-arrow-left text-xs"></i>
            <span>All projects</span>
          </router-link>

          <!-- Loading -->
          <div v-if="isLoading" class="flex flex-col items-center justify-center py-24">
            <div class="w-12 h-12 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.12] rounded-full flex items-center justify-center mb-4">
              <div class="w-6 h-6 border-2 border-blue-200 dark:border-blue-300/30 border-t-blue-600 dark:border-t-blue-300 rounded-full animate-spin"></div>
            </div>
            <p class="text-blue-950/70 dark:text-blue-100/70 text-sm transition-colors duration-300">Loading project...</p>
          </div>

          <!-- Not found -->
          <div v-else-if="!project" class="flex flex-col items-center justify-center py-24 text-center">
            <div class="w-16 h-16 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.12] rounded-full flex items-center justify-center mb-6">
              <i class="fas fa-folder-open text-2xl text-blue-950/40 dark:text-white/40"></i>
            </div>
            <h2 class="text-2xl font-semibold text-blue-950 dark:text-white mb-3 transition-colors duration-300">Project not found</h2>
            <p class="text-blue-950/70 dark:text-blue-100/70 mb-8 max-w-md transition-colors duration-300">We couldn't find this project. It may have been deleted.</p>
            <router-link
              :to="{ name: 'projects' }"
              class="inline-flex items-center gap-2 px-5 py-2.5 bg-white dark:bg-white/[0.06] hover:bg-blue-50 dark:hover:bg-white/[0.1] border border-blue-200/70 dark:border-white/[0.12] rounded-xl text-blue-950 dark:text-white font-medium text-sm transition-all duration-300"
            >
              <i class="fas fa-arrow-left text-sm"></i>
              <span>Back to projects</span>
            </router-link>
          </div>

          <!-- Hub -->
          <template v-else>
            <!-- Project header -->
            <section class="mb-8 md:mb-10">
              <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-blue-200/70 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-xs font-semibold text-blue-700 dark:text-blue-300 uppercase tracking-[0.18em] mb-4 transition-colors duration-300">Project workspace</p>
              <h1 class="text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-2 tracking-tight transition-colors duration-300">
                {{ project.name }}
              </h1>
              <p class="text-base text-blue-950/70 dark:text-blue-100/70 max-w-2xl transition-colors duration-300">
                {{ project.description || 'Build your product and run your business — all in one place. Choose a workspace to get started.' }}
              </p>
            </section>

            <!-- Category grid -->
            <section>
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                <ToolCategoryCard
                  v-for="tool in businessTools"
                  :key="tool.id"
                  :tool="tool"
                  :project-slug="projectSlug"
                  :build-status="buildStatus"
                />
              </div>
            </section>
          </template>
        </div>
      </main>
    </div>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { useProjectStore } from '../stores/projectStore'
import { ProjectService } from '../services/projectService'
import { useAuthStore } from '@/shared/stores/auth'
import { ToolCategoryCard } from '../components/organisms/hub'
import { businessTools } from '../utils/businessTools'
import { matchesSlug } from '../utils/slug'
import type { Project } from '../types/components'

const props = defineProps<{
  projectName: string
}>()

const projectStore = useProjectStore()
const authStore = useAuthStore()

const isInitializing = ref(true)

const projectSlug = computed(() => props.projectName)
const isLoading = computed(() => projectStore.loading || isInitializing.value)

const project = computed<Project | null>(() => {
  return projectStore.projects.find(p => matchesSlug(p.name, props.projectName)) || null
})

async function loadProject() {
  isInitializing.value = true
  try {
    if (!authStore.isAuthenticated) return
    if (projectStore.isAuthenticated !== authStore.isAuthenticated) {
      projectStore.setAuthenticated(authStore.isAuthenticated)
    }
    // Ensure the projects list is loaded so we can resolve the slug.
    if (!projectStore.projects.length) {
      await projectStore.fetchProjects()
    }
  } catch (error) {
    console.error('Failed to load project for hub:', error)
  } finally {
    isInitializing.value = false
  }
}

onMounted(loadProject)

// Reload if the route param changes (navigating between projects).
watch(() => props.projectName, loadProject)

// --- Initial AI build status ---
// Right after creation the backend runs the coding agent against the business
// description in the background. Poll the status endpoint while that build is
// in progress so the Build card can show it, and stop as soon as it settles.
const BUILD_STATUS_POLL_MS = 5000
const buildStatus = ref<'pending' | 'generating' | 'completed' | 'failed' | null>(null)
let buildStatusTimer: ReturnType<typeof setInterval> | null = null

function stopBuildStatusPolling() {
  if (buildStatusTimer) {
    clearInterval(buildStatusTimer)
    buildStatusTimer = null
  }
}

async function refreshBuildStatus() {
  const projectId = project.value?.id
  if (!projectId) return
  try {
    const status = await ProjectService.getProjectStatus(String(projectId))
    buildStatus.value = status.generation_status
    if (status.generation_status !== 'generating') {
      stopBuildStatusPolling()
    }
  } catch (error) {
    console.debug('Failed to fetch build status:', error)
    stopBuildStatusPolling()
  }
}

function startBuildStatusPolling() {
  stopBuildStatusPolling()
  refreshBuildStatus()
  buildStatusTimer = setInterval(refreshBuildStatus, BUILD_STATUS_POLL_MS)
}

// (Re)start polling whenever the hub resolves a project.
watch(
  () => project.value?.id,
  (projectId) => {
    buildStatus.value = null
    if (projectId) {
      startBuildStatusPolling()
    } else {
      stopBuildStatusPolling()
    }
  },
  { immediate: true }
)

onBeforeUnmount(stopBuildStatusPolling)
</script>
