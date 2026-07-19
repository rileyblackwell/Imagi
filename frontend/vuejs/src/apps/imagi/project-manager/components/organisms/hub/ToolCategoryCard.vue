<!--
  ToolCategoryCard.vue - A single workspace category on the project hub.

  Renders one BusinessTool (Build / Sell / Market / Operate) as a card that
  links either to the app builder or to the generic coming-soon tool page.
-->
<template>
  <component
    :is="isBuildLocked ? 'div' : 'router-link'"
    :to="isBuildLocked ? undefined : target"
    class="crisp-card group relative flex flex-col items-center text-center h-full px-6 pt-8 pb-6 rounded-2xl border transition-all duration-300"
    :class="[
      isBuildLocked
        ? 'building-card cursor-progress bg-white dark:bg-white/[0.05] border-blue-300/70 dark:border-blue-300/25'
        : ['bg-white dark:bg-white/[0.05] hover:-translate-y-1', accent.cardBorder],
    ]"
    :title="isBuildLocked ? 'Imagi is building your app — this card unlocks the moment the build finishes' : tool.name"
    :aria-disabled="isBuildLocked ? 'true' : undefined"
  >
    <!-- Soft accent glow on hover -->
    <div
      v-if="!isBuildLocked"
      class="pointer-events-none absolute -top-px inset-x-0 mx-auto w-40 h-40 rounded-full blur-3xl opacity-0 group-hover:opacity-100 bg-gradient-to-b to-transparent transition-opacity duration-500"
      :class="accent.glow"
    ></div>

    <!-- Moving sheen while building -->
    <div v-if="isBuildLocked" class="building-sheen pointer-events-none absolute inset-0 rounded-2xl overflow-hidden"></div>

    <!-- ==================== BUILDING STATE ==================== -->
    <template v-if="isBuildLocked">
      <span
        class="absolute top-3 right-3 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border border-blue-300/70 dark:border-blue-300/30 bg-blue-50/90 dark:bg-blue-400/10 text-[11px] font-semibold uppercase tracking-[0.14em] text-blue-700 dark:text-blue-200"
      >
        <span class="relative flex w-2 h-2">
          <span class="absolute inline-flex w-full h-full rounded-full bg-blue-500 dark:bg-blue-300 opacity-60 animate-ping"></span>
          <span class="relative inline-flex w-2 h-2 rounded-full bg-blue-600 dark:bg-blue-300"></span>
        </span>
        Building
      </span>

      <!-- Animated build icon: concentric pulsing rings behind a spinner ring -->
      <div class="relative w-16 h-16 flex items-center justify-center mb-5">
        <span class="absolute inset-0 rounded-2xl bg-blue-400/15 dark:bg-blue-300/10 animate-ping" style="animation-duration: 1.8s;"></span>
        <span class="absolute inset-1.5 rounded-2xl bg-blue-400/20 dark:bg-blue-300/15 animate-ping" style="animation-duration: 1.8s; animation-delay: .3s;"></span>
        <div class="relative w-14 h-14 rounded-2xl flex items-center justify-center border border-blue-300/70 dark:border-blue-300/25 bg-gradient-to-br from-blue-50 to-blue-100/60 dark:from-blue-400/10 dark:to-blue-500/10">
          <span class="absolute inset-0 rounded-2xl border-2 border-blue-500/70 dark:border-blue-300/60 border-t-transparent animate-spin" style="animation-duration: 1s;"></span>
          <i class="fas fa-wand-magic-sparkles text-lg text-blue-600 dark:text-blue-200"></i>
        </div>
      </div>

      <div class="relative flex-1">
        <h3 class="text-lg font-semibold text-blue-950 dark:text-white mb-1.5 tracking-tight">
          Building your app
        </h3>
        <p class="text-sm text-blue-950/70 dark:text-blue-100/70 leading-relaxed">
          Imagi is turning your business description into a tailored first version. This usually takes a moment.
        </p>
        <!-- Indeterminate progress track -->
        <div class="mt-4 h-1 w-full rounded-full bg-blue-100 dark:bg-white/[0.08] overflow-hidden">
          <div class="building-bar h-full w-1/3 rounded-full bg-gradient-to-r from-blue-400 via-blue-500 to-blue-400 dark:from-blue-300 dark:via-blue-400 dark:to-blue-300"></div>
        </div>
      </div>

      <div class="relative flex items-center justify-center gap-2 w-full text-sm font-medium mt-6 pt-4 border-t border-blue-200/60 dark:border-white/[0.1] text-blue-700/90 dark:text-blue-200/80">
        <i class="fas fa-lock text-[11px]"></i>
        <span>Unlocks when the build finishes</span>
      </div>
    </template>

    <!-- ==================== DEFAULT STATE ==================== -->
    <template v-else>
      <!-- Icon -->
      <div
        class="relative w-14 h-14 rounded-2xl flex items-center justify-center border mb-5 transition-transform duration-300 group-hover:scale-105"
        :class="[accent.iconWrap]"
      >
        <i :class="['fas', tool.icon, accent.iconText]" class="text-xl"></i>
      </div>

      <!-- Name + tagline -->
      <div class="relative flex-1">
        <h3 class="text-lg font-semibold text-blue-950 dark:text-white mb-1.5 tracking-tight transition-colors duration-300">
          {{ tool.name }}
        </h3>
        <p class="text-sm text-blue-950/70 dark:text-blue-100/70 leading-relaxed transition-colors duration-300">
          {{ tool.tagline }}
        </p>
      </div>

      <!-- CTA -->
      <div
        class="relative flex items-center justify-center gap-1.5 w-full text-sm font-medium mt-6 pt-4 border-t border-blue-200/60 dark:border-white/[0.1] transition-colors duration-300"
        :class="accent.link"
      >
        <span>{{ tool.status === 'available' ? 'Open workspace' : 'Preview' }}</span>
        <i class="fas fa-arrow-right text-xs group-hover:translate-x-1 transition-transform duration-200"></i>
      </div>
    </template>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { RouteLocationRaw } from 'vue-router'
import { accentClasses, type BusinessTool } from '../../../utils/businessTools'

const props = defineProps<{
  tool: BusinessTool
  projectSlug: string
  /** The project's generation_status; drives the Build card's "AI building" state. */
  buildStatus?: 'pending' | 'generating' | 'completed' | 'failed' | null
}>()

const accent = computed(() => accentClasses[props.tool.accent])

/**
 * The initial AI build is still running. While it is, the Build card is locked:
 * it shows a dedicated building state and cannot navigate into the workspace,
 * so users never enter a half-built project. Only the Build tool is gated.
 *
 * We lock strictly on 'generating' — the status the backend sets synchronously
 * the moment a build starts, before the create response returns. 'pending' is
 * deliberately excluded: it's the transient/legacy default, and locking on it
 * would trap older projects whose build never ran out of their own workspace.
 */
const isBuildLocked = computed(
  () => props.tool.id === 'build' && props.buildStatus === 'generating'
)

const target = computed<RouteLocationRaw>(() => {
  // "Build" points at the real workspace; everything else uses the generic
  // coming-soon tool route keyed by the tool's slug.
  if (props.tool.status === 'available') {
    return { name: props.tool.routeName, params: { projectName: props.projectSlug } }
  }
  return {
    name: props.tool.routeName,
    params: { projectName: props.projectSlug, category: props.tool.slug },
  }
})
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

.crisp-card:hover {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.04),
    0 2px 4px rgba(15, 23, 42, 0.07),
    0 8px 18px -4px rgba(15, 23, 42, 0.09),
    0 20px 40px -12px rgba(15, 23, 42, 0.14);
}

:global(.dark) .crisp-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}

:global(.dark) .crisp-card:hover {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.07),
    0 2px 4px rgba(0, 0, 0, 0.55),
    0 8px 18px -4px rgba(0, 0, 0, 0.5),
    0 20px 40px -12px rgba(0, 0, 0, 0.6);
}

/* ---- Building state ---- */
/* A soft, breathing ring around the card so "AI building" reads as active work. */
.building-card {
  animation: building-glow 2.4s ease-in-out infinite;
}

@keyframes building-glow {
  0%, 100% {
    box-shadow:
      0 0 0 1px rgba(59, 130, 246, 0.18),
      0 1px 2px rgba(15, 23, 42, 0.06),
      0 8px 22px -8px rgba(59, 130, 246, 0.28);
  }
  50% {
    box-shadow:
      0 0 0 1px rgba(59, 130, 246, 0.32),
      0 1px 2px rgba(15, 23, 42, 0.06),
      0 12px 34px -8px rgba(59, 130, 246, 0.45);
  }
}

/* Diagonal sheen sweeping across the card. */
.building-sheen::before {
  content: '';
  position: absolute;
  top: 0;
  left: -60%;
  width: 45%;
  height: 100%;
  background: linear-gradient(
    100deg,
    transparent,
    rgba(255, 255, 255, 0.55),
    transparent
  );
  transform: skewX(-18deg);
  animation: building-sweep 2.6s ease-in-out infinite;
}

:global(.dark) .building-sheen::before {
  background: linear-gradient(
    100deg,
    transparent,
    rgba(147, 197, 253, 0.14),
    transparent
  );
}

@keyframes building-sweep {
  0% { left: -60%; }
  60%, 100% { left: 120%; }
}

/* Indeterminate progress bar that slides back and forth. */
.building-bar {
  animation: building-bar 1.6s ease-in-out infinite;
}

@keyframes building-bar {
  0% { transform: translateX(-110%); }
  100% { transform: translateX(320%); }
}

@media (prefers-reduced-motion: reduce) {
  .building-card,
  .building-sheen::before,
  .building-bar {
    animation: none;
  }
}
</style>
