<!--
  ProjectHub.vue - Project Overview / Workspace Hub

  This is the landing page for a single project (business). From here the user
  chooses how to work on it:
    - Build -> the AI app builder (real, existing workspace)
    - Sell -> sales tools (general template, coming soon)
    - Market -> marketing tools (general template, coming soon)
    - Operate -> finance & operations tools (general template, coming soon)

  The categories are driven by utils/businessTools.ts. This view is a template
  shell — it does not implement any of the specific tools.
-->
<template>
  <DefaultLayout>
    <div class="hub-page page-canvas brand-selection crisp-text relative transition-colors duration-500 min-h-screen overflow-hidden font-body">
      <!-- Grain texture over the porcelain canvas -->
      <div class="grain-overlay absolute inset-0 z-[1] pointer-events-none" aria-hidden="true"></div>

      <!-- Atmosphere: one soft baby-blue wash behind the header -->
      <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div class="page-glow-cool absolute -top-40 left-1/2 -translate-x-1/2 w-[760px] h-[440px]"></div>
      </div>

      <main class="relative z-10 flex flex-col px-6 sm:px-8 lg:px-12 pt-20 pb-12 min-h-screen">
        <div class="max-w-6xl mx-auto w-full">

          <!-- Back link -->
          <router-link
            :to="{ name: 'projects' }"
            class="inline-flex items-center gap-2 rounded-full text-sm font-medium text-blue-950/70 dark:text-blue-100/55 hover:text-blue-950 dark:hover:text-white transition-colors duration-200 mb-6 focus-ring"
          >
            <i class="fas fa-arrow-left text-xs"></i>
            <span>All projects</span>
          </router-link>

          <!-- Loading -->
          <div v-if="isLoading" class="flex flex-col items-center justify-center py-24">
            <div class="w-12 h-12 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.14] rounded-full flex items-center justify-center mb-4">
              <div class="w-6 h-6 border-2 border-blue-200 dark:border-blue-300/30 border-t-blue-600 dark:border-t-blue-300 rounded-full animate-spin"></div>
            </div>
            <p class="text-blue-950/70 dark:text-blue-100/70 text-sm transition-colors duration-300">Loading project...</p>
          </div>

          <!-- Not found -->
          <div v-else-if="!project" class="flex flex-col items-center justify-center py-24 text-center">
            <div class="w-16 h-16 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.14] rounded-full flex items-center justify-center mb-6">
              <i class="fas fa-folder-open text-2xl text-blue-950/40 dark:text-blue-100/40"></i>
            </div>
            <h2 class="text-2xl font-semibold tracking-tight text-blue-950 dark:text-white mb-3 transition-colors duration-300">Project not found</h2>
            <p class="text-blue-950/65 dark:text-blue-100/65 mb-8 max-w-md transition-colors duration-300">We couldn't find this project. It may have been deleted.</p>
            <router-link
              :to="{ name: 'projects' }"
              class="inline-flex items-center gap-2 px-5 py-2.5 rounded-full border border-blue-950/[0.14] text-blue-950/80 hover:text-blue-950 hover:border-blue-950/30 hover:bg-blue-950/[0.03] dark:border-white/[0.16] dark:text-blue-100/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06] font-medium text-sm transition-colors duration-200 focus-ring"
            >
              <i class="fas fa-arrow-left text-sm"></i>
              <span>Back to projects</span>
            </router-link>
          </div>

          <!-- Hub -->
          <template v-else>
            <!-- Project header -->
            <section class="rise-item flex flex-col items-center text-center mb-10 md:mb-14" style="animation-delay: 0ms">
              <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-blue-200/70 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-xs font-semibold text-blue-700 dark:text-blue-300 uppercase tracking-[0.18em] mb-5 transition-colors duration-300">Project workspace</p>
              <h1 class="font-display text-4xl sm:text-5xl lg:text-6xl font-semibold text-blue-950 dark:text-white mb-4 tracking-[-0.02em] leading-[1.05] text-balance transition-colors duration-300">
                {{ project.name }}
              </h1>
              <p class="text-base sm:text-lg text-blue-950/65 dark:text-blue-100/65 max-w-2xl leading-relaxed text-pretty transition-colors duration-300">
                {{ project.description || 'Build your product and run your business — all in one place. Choose a workspace to get started.' }}
              </p>
              <div class="mt-7 h-px w-16 bg-gradient-to-r from-transparent via-blue-300/60 dark:via-blue-300/25 to-transparent" aria-hidden="true"></div>
            </section>

            <!-- Category grid -->
            <section class="rise-item" style="animation-delay: 90ms">
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 sm:gap-6">
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
import { ref, computed, onBeforeUnmount, watch } from 'vue'
import { DefaultLayout } from '@/shared/layouts'

import { ProjectService } from '@/apps/imagi/build/services/projectService'

import { ToolCategoryCard } from '../components/organisms/hub'
import { businessTools } from '../utils/businessTools'
import { useProjectFromSlug } from '@/apps/imagi/shared'

const props = defineProps<{
  projectName: string
}>()

const projectSlug = computed(() => props.projectName)
const { project, isLoading } = useProjectFromSlug(projectSlug, 'the project hub')

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

<style scoped>

/* Soft baby-blue wash behind the page header */
.page-glow-cool {
  background: radial-gradient(closest-side, rgba(158, 205, 243, 0.2), rgba(158, 205, 243, 0.06) 55%, transparent 75%);
  filter: blur(48px);
}

.dark .page-glow-cool {
  background: radial-gradient(closest-side, rgba(96, 165, 250, 0.08), rgba(96, 165, 250, 0.02) 55%, transparent 75%);
}
</style>

<!-- Unscoped: brand-tinted text selection on the hub page -->

