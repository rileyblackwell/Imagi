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
    <div class="tool-page relative transition-colors duration-500 min-h-screen overflow-hidden font-body">
      <!-- Grain texture over the porcelain canvas -->
      <div class="grain-overlay absolute inset-0 z-[1] pointer-events-none" aria-hidden="true"></div>

      <!-- Atmosphere: one soft apricot wash behind the header -->
      <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div class="page-glow-warm absolute -top-40 left-1/2 -translate-x-1/2 w-[760px] h-[440px]"></div>
      </div>

      <main class="relative z-10 flex flex-col px-6 sm:px-8 lg:px-12 pt-20 pb-12 min-h-screen">
        <div class="max-w-5xl mx-auto w-full">

          <!-- Back link -->
          <router-link
            :to="{ name: 'project-hub', params: { projectName } }"
            class="inline-flex items-center gap-2 rounded-full text-sm font-medium text-blue-950/70 dark:text-blue-100/55 hover:text-blue-950 dark:hover:text-white transition-colors duration-200 mb-6 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
          >
            <i class="fas fa-arrow-left text-xs"></i>
            <span>Project workspace</span>
          </router-link>

          <!-- Unknown category -->
          <div v-if="!tool" class="flex flex-col items-center justify-center py-24 text-center">
            <div class="w-16 h-16 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.14] rounded-full flex items-center justify-center mb-6">
              <i class="fas fa-circle-question text-2xl text-blue-950/40 dark:text-blue-100/40"></i>
            </div>
            <h2 class="text-2xl font-semibold tracking-tight text-blue-950 dark:text-white mb-3 transition-colors duration-300">Tool not found</h2>
            <router-link
              :to="{ name: 'project-hub', params: { projectName } }"
              class="inline-flex items-center gap-2 px-5 py-2.5 rounded-full border border-blue-950/[0.14] text-blue-950/80 hover:text-blue-950 hover:border-blue-950/30 hover:bg-blue-950/[0.03] dark:border-white/[0.16] dark:text-blue-100/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06] font-medium text-sm transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
            >
              <i class="fas fa-arrow-left text-sm"></i>
              <span>Back to workspace</span>
            </router-link>
          </div>

          <template v-else>
            <!-- Header -->
            <section class="rise-item flex flex-col sm:flex-row sm:items-center gap-5 mb-8" style="animation-delay: 0ms">
              <div
                class="w-16 h-16 rounded-2xl flex items-center justify-center border flex-shrink-0 transition-colors duration-300"
                :class="accent.iconWrap"
              >
                <i :class="['fas', tool.icon, accent.iconText]" class="text-2xl"></i>
              </div>
              <div>
                <div class="flex items-center gap-3 mb-1.5">
                  <h1 class="font-display text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white tracking-[-0.02em] leading-[1.05] transition-colors duration-300">{{ tool.name }}</h1>
                  <span class="inline-flex items-center px-2.5 py-1 rounded-full border border-blue-950/10 dark:border-white/15 bg-blue-950/[0.03] dark:bg-white/[0.04] text-[11px] font-semibold uppercase tracking-[0.14em] text-blue-950/70 dark:text-blue-100/55 transition-colors duration-300">Coming soon</span>
                </div>
                <p class="text-base text-blue-950/65 dark:text-blue-100/65 max-w-2xl leading-relaxed transition-colors duration-300">{{ tool.description }}</p>
              </div>
            </section>

            <!-- Planned capabilities -->
            <section class="rise-item mb-8" style="animation-delay: 90ms">
              <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border text-xs font-semibold uppercase tracking-[0.18em] mb-4 transition-colors duration-300" :class="accent.badge">What's coming</p>
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div
                  v-for="feature in tool.features"
                  :key="feature.name"
                  class="crisp-card p-5 rounded-2xl bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm border border-blue-200/70 dark:border-blue-300/[0.14] transition-colors duration-300"
                >
                  <div class="w-10 h-10 rounded-xl flex items-center justify-center border mb-3 transition-colors duration-300" :class="accent.iconWrap">
                    <i :class="['fas', feature.icon, accent.iconText]"></i>
                  </div>
                  <h3 class="text-base font-semibold tracking-tight text-blue-950 dark:text-white mb-1 transition-colors duration-300">{{ feature.name }}</h3>
                  <p class="text-sm text-blue-950/65 dark:text-blue-100/65 leading-snug transition-colors duration-300">{{ feature.description }}</p>
                </div>
              </div>
            </section>

            <!-- Placeholder notice -->
            <section class="rise-item" style="animation-delay: 180ms">
              <div class="crisp-card p-6 md:p-8 rounded-2xl bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm border border-blue-200/70 dark:border-blue-300/[0.14] text-center transition-colors duration-300">
                <div class="w-12 h-12 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.14] rounded-full flex items-center justify-center mx-auto mb-4">
                  <i class="fas fa-screwdriver-wrench text-xl text-blue-950/40 dark:text-blue-100/40"></i>
                </div>
                <h3 class="text-lg font-semibold tracking-tight text-blue-950 dark:text-white mb-2 transition-colors duration-300">We're building this workspace</h3>
                <p class="text-sm text-blue-950/65 dark:text-blue-100/65 max-w-md mx-auto mb-6 transition-colors duration-300">
                  {{ tool.name }} tools aren't available yet. In the meantime, you can start building your product with the app builder.
                </p>
                <router-link
                  :to="{ name: 'builder-workspace', params: { projectName } }"
                  class="group inline-flex items-center justify-center gap-3 px-7 py-3 rounded-full font-medium text-base bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-colors duration-200 shadow-[0_1px_2px_rgba(23,37,84,0.2),0_3px_8px_-2px_rgba(23,37,84,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
                >
                  <i class="fas fa-wand-magic-sparkles"></i>
                  <span>Open the app builder</span>
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
/* Warm porcelain canvas fading to white so the page hands off to the footer
   (footer is bg-white / dark #0a0a0a) — matches Home.vue */
.tool-page {
  background: linear-gradient(180deg, #fdf9f2 0%, #faf7f1 45%, #ffffff 100%);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

.dark .tool-page {
  background: linear-gradient(180deg, #0c0c0e 0%, #0a0b0f 50%, #0a0a0a 100%);
}

/* Fine film grain keeps large soft gradients from banding and adds texture */
.grain-overlay {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E");
  background-size: 160px 160px;
  opacity: 0.035;
  mix-blend-mode: multiply;
}

.dark .grain-overlay {
  opacity: 0.05;
  mix-blend-mode: overlay;
}

/* Soft apricot wash behind the page header */
.page-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.13), rgba(251, 146, 60, 0.04) 55%, transparent 75%);
  filter: blur(48px);
}

.dark .page-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.07), rgba(251, 146, 60, 0.02) 55%, transparent 75%);
}

/* Page-load rise: header and sections fade up in sequence */
.rise-item {
  animation: rise-up 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes rise-up {
  from {
    opacity: 0;
    transform: translateY(18px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .rise-item {
    animation: none;
  }
}

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
</style>

<!-- Unscoped: brand-tinted text selection on the tool page -->
<style>
.tool-page ::selection {
  background: rgba(158, 205, 243, 0.55);
  color: #172554;
}

.dark .tool-page ::selection {
  background: rgba(96, 165, 250, 0.4);
  color: #eff6ff;
}
</style>
