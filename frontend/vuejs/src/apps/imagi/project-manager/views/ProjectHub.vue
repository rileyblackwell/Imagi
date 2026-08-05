<!--
  ProjectHub.vue — a single project (business), and the four ways to work on it:
    - Build   -> the AI app builder
    - Sell    -> products, checkout, orders, customers
    - Market  -> campaigns, audience, ads, inbox
    - Operate -> finance, invoicing, tasks

  The modules are driven by utils/businessTools.ts. This view is the shell — it
  does not implement any of the tools themselves.

  Design: the editorial surface, same as the projects list it is reached from —
  a header and four ruled columns, mirroring how the home page introduces the
  same four modules. Everything visual comes from shared/styles/editorial.css.
-->
<template>
  <DefaultLayout>
    <div class="editorial hub-page relative min-h-screen font-body">
      <div class="grain-overlay absolute inset-0 z-[1] pointer-events-none" aria-hidden="true"></div>

      <main class="relative z-10">
        <section class="relative pt-28 sm:pt-36 md:pt-40 pb-20 md:pb-28">
          <div class="section-shell">

            <!-- Back link -->
            <router-link :to="{ name: 'projects' }" class="back">
              <svg class="back__arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M19 12H5M11 18l-6-6 6-6" />
              </svg>
              <span>All projects</span>
            </router-link>

            <!-- Loading -->
            <p v-if="isLoading" class="state">
              <span class="spinner" aria-hidden="true"></span>
              <span>Loading project&hellip;</span>
            </p>

            <!-- Not found -->
            <div v-else-if="!project" class="mt-16 max-w-xl">
              <p class="eyebrow">
                <span class="eyebrow__mark" aria-hidden="true"></span>
                <span class="eyebrow__rule" aria-hidden="true"></span>
                <span>Not found</span>
              </p>
              <h1 class="display mt-6 text-4xl sm:text-5xl">This project isn't here</h1>
              <p class="lede mt-6 text-lg">
                We couldn't find it. It may have been deleted, or the link may be out of date.
              </p>
              <router-link :to="{ name: 'projects' }" class="btn-outline mt-9">
                Back to projects
              </router-link>
            </div>

            <!-- Hub -->
            <template v-else>
              <!-- Project header -->
              <div class="rise-item mt-12 md:mt-16 md:flex md:items-end md:justify-between gap-12 lg:gap-16">
                <div class="max-w-[36rem]">
                  <p class="eyebrow">
                    <span class="eyebrow__rule" aria-hidden="true"></span>
                    <span>Project</span>
                  </p>
                  <h1 class="display mt-7 text-[2.5rem] sm:text-5xl md:text-[3.6rem]">
                    {{ project.name }}
                  </h1>
                </div>
                <p class="rise-item lede mt-7 md:mt-0 md:max-w-sm md:pb-3 text-lg" style="animation-delay: 90ms">
                  {{ project.description || 'Build the product and run the business behind it — all in one project. Pick a module to get started.' }}
                </p>
              </div>

              <!-- Modules -->
              <div class="rise-item mt-16 md:mt-20" style="animation-delay: 180ms">
                <div class="section-rule mb-14 md:mb-16" aria-hidden="true"></div>
                <div class="rule-cols rule-cols--4">
                  <ToolCategoryCard
                    v-for="tool in businessTools"
                    :key="tool.id"
                    :tool="tool"
                    :project-slug="projectSlug"
                    :build-status="buildStatus"
                  />
                </div>
              </div>
            </template>
          </div>
        </section>
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
// in progress so the Build module can show it, and stop as soon as it settles.
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
/* The one step back up the hierarchy. Quieter than a button, because it is a
   trail rather than an action. */
.back {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--ink-40);
  transition: color 0.18s ease;
}

.back:hover {
  color: var(--ink);
}

.back:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 3px;
}

.back__arrow {
  width: 0.9rem;
  height: 0.9rem;
  transition: transform 0.18s ease;
}

.back:hover .back__arrow {
  transform: translateX(-3px);
}

.state {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin-top: 5rem;
  font-size: 0.9375rem;
  color: var(--ink-55);
}

.spinner {
  flex: none;
  width: 1rem;
  height: 1rem;
  border: 1.5px solid var(--accent);
  border-top-color: transparent;
  border-radius: 999px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .spinner {
    animation: none;
  }

  .back:hover .back__arrow {
    transform: none;
  }
}
</style>
