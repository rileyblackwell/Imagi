<!--
  ToolCategory.vue - Generic "coming soon" template for a business tool.

  Drives the coming-soon pages (Sell / Operate) from utils/businessTools.ts.
  It shows the category's purpose and a preview of the planned capabilities.
  Tools with their own workspace (Build, Market) register static routes that
  take precedence over this view's :category param.

  Route: /imagi/project/:projectName/:category
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
        <div class="max-w-5xl mx-auto w-full">

          <!-- Back link -->
          <router-link
            :to="{ name: 'project-hub', params: { projectName } }"
            class="inline-flex items-center gap-2 text-sm font-medium text-blue-950/60 dark:text-blue-100/60 hover:text-blue-950 dark:hover:text-white transition-colors duration-200 mb-6"
          >
            <i class="fas fa-arrow-left text-xs"></i>
            <span>Project workspace</span>
          </router-link>

          <!-- Unknown category -->
          <div v-if="!tool" class="flex flex-col items-center justify-center py-24 text-center">
            <div class="w-16 h-16 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.12] rounded-full flex items-center justify-center mb-6">
              <i class="fas fa-circle-question text-2xl text-blue-950/40 dark:text-white/40"></i>
            </div>
            <h2 class="text-2xl font-semibold text-blue-950 dark:text-white mb-3 transition-colors duration-300">Tool not found</h2>
            <router-link
              :to="{ name: 'project-hub', params: { projectName } }"
              class="inline-flex items-center gap-2 px-5 py-2.5 bg-white dark:bg-white/[0.06] hover:bg-blue-50 dark:hover:bg-white/[0.1] border border-blue-200/70 dark:border-white/[0.12] rounded-xl text-blue-950 dark:text-white font-medium text-sm transition-all duration-300"
            >
              <i class="fas fa-arrow-left text-sm"></i>
              <span>Back to workspace</span>
            </router-link>
          </div>

          <template v-else>
            <!-- Header -->
            <section class="flex flex-col sm:flex-row sm:items-center gap-5 mb-8">
              <div
                class="w-16 h-16 rounded-2xl flex items-center justify-center border flex-shrink-0 transition-colors duration-300"
                :class="accent.iconWrap"
              >
                <i :class="['fas', tool.icon, accent.iconText]" class="text-2xl"></i>
              </div>
              <div>
                <div class="flex items-center gap-3 mb-1.5">
                  <h1 class="text-3xl font-semibold text-blue-950 dark:text-white tracking-tight transition-colors duration-300">{{ tool.name }}</h1>
                  <span class="inline-flex items-center px-2.5 py-1 rounded-full border border-blue-950/10 dark:border-white/15 bg-blue-950/[0.03] dark:bg-white/[0.04] text-[11px] font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-white/50 transition-colors duration-300">Coming soon</span>
                </div>
                <p class="text-base text-blue-950/70 dark:text-blue-100/70 max-w-2xl transition-colors duration-300">{{ tool.description }}</p>
              </div>
            </section>

            <!-- Planned capabilities -->
            <section class="mb-8">
              <p class="inline-flex items-center px-3 py-1 rounded-full border text-xs font-semibold uppercase tracking-[0.18em] mb-4 transition-colors duration-300" :class="accent.badge">What's coming</p>
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div
                  v-for="feature in tool.features"
                  :key="feature.name"
                  class="crisp-card p-5 rounded-2xl bg-white dark:bg-white/[0.05] border border-blue-200/70 dark:border-blue-300/[0.16] transition-colors duration-300"
                >
                  <div class="w-10 h-10 rounded-xl flex items-center justify-center border mb-3 transition-colors duration-300" :class="accent.iconWrap">
                    <i :class="['fas', feature.icon, accent.iconText]"></i>
                  </div>
                  <h3 class="text-base font-semibold text-blue-950 dark:text-white mb-1 transition-colors duration-300">{{ feature.name }}</h3>
                  <p class="text-sm text-blue-950/70 dark:text-blue-100/70 leading-snug transition-colors duration-300">{{ feature.description }}</p>
                </div>
              </div>
            </section>

            <!-- Placeholder notice -->
            <section>
              <div class="crisp-card p-6 md:p-8 rounded-2xl bg-white dark:bg-white/[0.05] border border-blue-200/70 dark:border-blue-300/[0.16] text-center transition-colors duration-300">
                <div class="w-12 h-12 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.12] rounded-full flex items-center justify-center mx-auto mb-4">
                  <i class="fas fa-screwdriver-wrench text-xl text-blue-950/40 dark:text-white/40"></i>
                </div>
                <h3 class="text-lg font-semibold text-blue-950 dark:text-white mb-2 transition-colors duration-300">We're building this workspace</h3>
                <p class="text-sm text-blue-950/70 dark:text-blue-100/70 max-w-md mx-auto mb-6 transition-colors duration-300">
                  {{ tool.name }} tools aren't available yet. In the meantime, you can start building your product with the app builder.
                </p>
                <router-link
                  :to="{ name: 'builder-workspace', params: { projectName } }"
                  class="btn-3d btn-accent group relative inline-flex items-center justify-center gap-3 px-7 py-3 text-blue-950 rounded-full font-medium text-base overflow-hidden border border-white/60 dark:border-white/30"
                >
                  <span class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent"></span>
                  <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-blue-900/15 to-transparent"></span>
                  <i class="fas fa-wand-magic-sparkles relative"></i>
                  <span class="relative">Open the app builder</span>
                </router-link>
              </div>
            </section>
          </template>
        </div>
      </main>
    </div>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { getToolBySlug, accentClasses } from '../utils/businessTools'

const props = defineProps<{
  projectName: string
  category: string
}>()

const tool = computed(() => getToolBySlug(props.category))
const accent = computed(() => accentClasses[tool.value?.accent ?? 'blue'])
</script>

<style scoped>
/* Crisp, sharply-defined card matching Home/About - hairline edge + tight layered shadow */
.crisp-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

:global(.dark) .crisp-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}

.btn-3d {
  transform: translateY(0) translateZ(0);
  transition: transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease;
  box-shadow:
    0 1px 2px rgba(30, 58, 138, 0.14),
    0 4px 10px -2px rgba(30, 58, 138, 0.16),
    0 10px 20px -6px rgba(30, 58, 138, 0.18),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.12);
}

.btn-3d:active {
  transform: translateY(0) translateZ(0);
  transition-duration: 0.1s;
}

.btn-accent {
  background: linear-gradient(155deg, #dbeeff 0%, #b7ddf7 55%, #9ecdf3 100%);
}

:global(.dark) .btn-accent {
  background: linear-gradient(155deg, #dbeeff 0%, #b7ddf7 55%, #9ecdf3 100%);
}

:global(.dark) .btn-3d {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 10px 20px -6px rgba(0, 0, 0, 0.5),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.18);
}
</style>
