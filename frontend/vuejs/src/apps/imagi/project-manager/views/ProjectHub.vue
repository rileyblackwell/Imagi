<!--
  ProjectHub.vue — a single project (business), and the four ways to work on it:
    - Build   -> the AI app builder
    - Sell    -> products, checkout, orders, customers
    - Market  -> campaigns, audience, ads, inbox
    - Operate -> finance, invoicing, tasks

  The modules are driven by utils/businessTools.ts. This view is the shell — it
  does not implement any of the tools themselves.

  Design: the Spotlight stage, same as the projects list it is reached from —
  the project's name lit in an opener, then four cards mirroring how the home
  page introduces the same four modules.
-->
<template>
  <div class="spotlight hub-root">
  <DefaultLayout>
    <div class="editorial hub-page relative min-h-screen">
      <main class="relative">
        <section class="sl-opener hub-stage">
          <div class="sl-spot" aria-hidden="true"></div>
          <div class="sl-dots" aria-hidden="true"></div>
          <div class="sl-wrap">

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
            <div v-else-if="!project" class="sl-opener__inner hub-head">
              <p class="sl-eyebrow sl-pill">
                <span class="sl-pip" aria-hidden="true"></span>
                <span>Not found</span>
              </p>
              <h1 class="sl-display hub-missing">This project isn't here</h1>
              <p class="sl-lede">
                We couldn't find it. It may have been deleted, or the link may be out of date.
              </p>
              <router-link :to="{ name: 'projects' }" class="btn-outline mt-9">
                Back to projects
              </router-link>
            </div>

            <!-- Hub -->
            <template v-else>
              <!-- Project header -->
              <div class="sl-opener__inner hub-head">
                <p class="rise-item sl-eyebrow sl-pill">
                  <span class="sl-pip" aria-hidden="true"></span>
                  <span>Project</span>
                </p>
                <h1 class="rise-item sl-display sl-h1 hub-title" style="animation-delay: 60ms">
                  {{ project.name }}
                </h1>
                <p class="rise-item sl-lede" style="animation-delay: 120ms">
                  {{ project.description || 'Build the product and run the business behind it — all in one project. Pick a module to get started.' }}
                </p>
              </div>

              <!-- Modules -->
              <div class="rise-item sl-cards hub-modules" style="animation-delay: 180ms">
                <ToolCategoryCard
                  v-for="tool in businessTools"
                  :key="tool.id"
                  :tool="tool"
                  :project-slug="projectSlug"
                  :build-status="buildStatus"
                />
              </div>
            </template>
          </div>
        </section>
      </main>
    </div>
  </DefaultLayout>
  </div>
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
/* The stage starts a little higher than a marketing opener: the back link
   sits above the pill. */
.sl-opener.hub-stage {
  padding-top: calc(3.5rem + clamp(32px, 4vw, 56px));
  padding-bottom: clamp(72px, 9vw, 120px);
}

.hub-head {
  margin-top: clamp(28px, 4vw, 48px);
}

.sl-opener .hub-title {
  max-width: 14ch;
  font-size: clamp(44px, 7.6vw, 104px);
  overflow-wrap: anywhere;
}

.hub-missing {
  font-size: clamp(36px, 5vw, 60px);
  line-height: 1;
  letter-spacing: -0.03em;
}

.spotlight .hub-modules {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

@media (max-width: 1100px) {
  .spotlight .hub-modules {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .spotlight .hub-modules {
    grid-template-columns: minmax(0, 1fr);
  }
}

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
  color: var(--sl-faint);
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
  justify-content: center;
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
