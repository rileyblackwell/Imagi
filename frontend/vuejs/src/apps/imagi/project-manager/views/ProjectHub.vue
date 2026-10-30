<!--
  ProjectHub.vue — a single project (business), and the four ways to work on it:
    - Build   -> the AI app builder
    - Sell    -> products, checkout, orders, customers
    - Market  -> campaigns, audience, ads, inbox
    - Operate -> finance, invoicing, tasks

  The modules are driven by utils/businessTools.ts. This view is the shell — it
  does not implement any of the tools themselves.

  Design: the Spotlight stage, same as the projects list it is reached from —
  the project's name in an opener, then the modules in the product's two
  halves: Build as one lit panel, and Sell / Market / Operate stacked beside it
  as the tools that run the business.
-->
<template>
  <div class="spotlight">
  <DefaultLayout>
    <div class="editorial relative min-h-screen">
      <main class="relative">
        <!-- The stage starts a little higher than a marketing opener: the back
             link sits above the pill. -->
        <section class="sl-opener !pb-[clamp(72px,9vw,120px)] !pt-[calc(3.5rem+clamp(32px,4vw,56px))]">
          <div class="sl-spot" aria-hidden="true"></div>
          <div class="sl-dots" aria-hidden="true"></div>
          <div class="sl-wrap">

            <!-- Back link: the one step back up the hierarchy. Quieter than a
                 button, because it is a trail rather than an action. -->
            <router-link
              :to="{ name: 'projects' }"
              class="group inline-flex items-center gap-2 text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-sl-faint [transition:color_0.18s_ease]
                hover:text-ed-ink focus-visible:!outline-ed-accent"
            >
              <svg
                class="h-[0.9rem] w-[0.9rem] [transition:transform_0.18s_ease] group-hover:-translate-x-[3px] motion-reduce:group-hover:transform-none"
                viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"
              >
                <path d="M19 12H5M11 18l-6-6 6-6" />
              </svg>
              <span>All projects</span>
            </router-link>

            <!-- Loading -->
            <p v-if="isLoading" class="mt-20 flex items-center justify-center gap-[0.7rem] text-[0.9375rem] text-ed-ink-55">
              <span class="spinner h-4 w-4 flex-none rounded-[999px] border-[1.5px] border-ed-accent border-t-transparent" aria-hidden="true"></span>
              <span>Loading project&hellip;</span>
            </p>

            <!-- Not found -->
            <div v-else-if="!project" :class="HEAD">
              <p class="sl-eyebrow sl-pill">
                <span class="sl-pip" aria-hidden="true"></span>
                <span>Not found</span>
              </p>
              <h1 class="sl-display text-[clamp(36px,5vw,60px)] leading-none tracking-[-0.03em]">This project isn't here</h1>
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
              <div :class="HEAD">
                <p class="rise-item sl-eyebrow sl-pill">
                  <span class="sl-pip" aria-hidden="true"></span>
                  <span>Project</span>
                </p>
                <h1 class="rise-item sl-display sl-h1 max-w-[16ch] !text-[clamp(44px,6.4vw,84px)] [overflow-wrap:anywhere]" style="animation-delay: 60ms">
                  {{ project.name }}
                </h1>
                <p class="rise-item sl-lede !ml-0 !max-w-[620px] !text-[18px]" style="animation-delay: 120ms">
                  {{ project.description || 'Build your app, and when you want it to become a business, run it from the same project. Pick a module to get started.' }}
                </p>
              </div>

              <!-- Modules, in the product's two halves: Build the product on
                   the left, the tools that run the business on the right. -->
              <div
                class="rise-item mt-[clamp(40px,5vw,64px)] grid grid-cols-[minmax(0,1.08fr)_minmax(0,1fr)] gap-[22px] text-left max-[900px]:grid-cols-[minmax(0,1fr)] max-[900px]:gap-[36px]"
                style="animation-delay: 180ms"
              >
                <section v-if="buildTool" class="hub-half flex min-w-0 flex-col" aria-labelledby="hub-half-build">
                  <h2 id="hub-half-build" :class="HALF_LABEL">
                    <b :class="HALF_NAME">Build</b><span>the app</span>
                  </h2>
                  <ToolCategoryCard
                    :tool="buildTool"
                    :project-slug="projectSlug"
                    :build-status="buildStatus"
                    layout="feature"
                  />
                </section>
                <section class="hub-half flex min-w-0 flex-col" aria-labelledby="hub-half-run">
                  <h2 id="hub-half-run" :class="HALF_LABEL">
                    <b :class="HALF_NAME">Run</b><span>it as a business</span>
                  </h2>
                  <div class="flex flex-1 flex-col gap-[14px]">
                    <ToolCategoryCard
                      v-for="tool in runTools"
                      :key="tool.id"
                      :tool="tool"
                      :project-slug="projectSlug"
                      :build-status="buildStatus"
                    />
                  </div>
                </section>
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

// The opener's header, left-aligned rather than .sl-opener__inner's centre.
const HEAD = 'sl-opener__inner mt-[clamp(28px,4vw,48px)] !items-start !text-left'
// "Build — the app", "Run — it as a business": the homepage's two halves,
// named on a hairline (::after) above each column.
const HALF_LABEL =
  "hub-half__label mb-[14px] ml-[4px] flex items-center gap-[12px] text-[13px] font-normal text-sl-faint after:h-px after:flex-1 after:bg-sl-line after:content-['']"
const HALF_NAME = 'font-sl-display text-[15px] font-semibold tracking-[-0.01em] text-sl-text'

// Build is the half that makes the product; every other module runs the business.
const buildTool = businessTools.find(tool => tool.id === 'build')
const runTools = businessTools.filter(tool => tool.id !== 'build')
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
/* The spinner's turn. Keyframes stay CSS: scoped keyframe names are hashed,
   so a utility can't reference them. */
.spinner {
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
}
</style>
