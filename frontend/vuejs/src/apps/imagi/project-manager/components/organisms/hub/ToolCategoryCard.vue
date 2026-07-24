<!--
  ToolCategoryCard.vue - A single workspace category on the project hub.

  Renders one BusinessTool (Build / Sell / Market / Operate) as a card that
  links either to the app builder or to the generic coming-soon tool page.
-->
<template>
  <component
    :is="isBuildLocked ? 'div' : 'router-link'"
    :to="isBuildLocked ? undefined : target"
    class="crisp-card group relative flex flex-col h-full p-7 rounded-2xl border backdrop-blur-sm transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
    :class="[
      isBuildLocked
        ? 'building-card items-center text-center cursor-progress bg-white/85 dark:bg-white/[0.045] border-blue-300/70 dark:border-blue-300/25'
        : ['items-start text-left bg-white/90 dark:bg-white/[0.045] hover:-translate-y-1', tone.card],
    ]"
    :title="isBuildLocked ? 'Imagi is building your app — this card unlocks the moment the build finishes' : tool.name"
    :aria-disabled="isBuildLocked ? 'true' : undefined"
  >
    <!-- ==================== BUILDING STATE ==================== -->
    <template v-if="isBuildLocked">
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
        <p class="text-sm text-blue-950/65 dark:text-blue-100/65 leading-relaxed">
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
      <!-- Icon chip: solid ink with a porcelain glyph and a soft top sheen -->
      <div
        class="card-tile relative w-12 h-12 rounded-xl flex items-center justify-center mb-7 transition-transform duration-300"
        :class="tone.tile"
      >
        <span class="tile-sheen pointer-events-none absolute inset-0 rounded-xl" aria-hidden="true"></span>
        <i :class="['fas', tool.icon, tone.glyph]" class="relative text-lg"></i>
      </div>

      <!-- Name + tagline -->
      <h3 class="relative text-[17px] font-semibold text-blue-950 dark:text-white mb-1.5 tracking-[-0.01em] transition-colors duration-300">
        {{ tool.name }}
      </h3>
      <p class="relative text-sm text-blue-950/55 dark:text-blue-100/55 leading-relaxed transition-colors duration-300">
        {{ tool.tagline }}
      </p>

      <!-- CTA: muted ink at rest, resolves to full ink on hover -->
      <div
        class="relative flex items-center w-full text-[13px] font-medium mt-auto pt-5 border-t border-blue-950/[0.06] dark:border-white/[0.07] text-blue-950/55 dark:text-blue-100/50 group-hover:text-blue-950 dark:group-hover:text-white transition-colors duration-200"
      >
        <span>{{ tool.status === 'available' ? 'Open workspace' : 'Preview' }}</span>
        <i class="fas fa-arrow-right text-[11px] ml-auto group-hover:translate-x-0.5 transition-transform duration-200"></i>
      </div>
    </template>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { RouteLocationRaw } from 'vue-router'
import { hubCardTones, type BusinessTool } from '../../../utils/businessTools'

const props = defineProps<{
  tool: BusinessTool
  projectSlug: string
  /** The project's generation_status; drives the Build card's "AI building" state. */
  buildStatus?: 'pending' | 'generating' | 'completed' | 'failed' | null
}>()

// Every hub card wears the restrained ink tone (solid ink chip, neutral border,
// muted ink CTA) so the four repeated cards stay calm and professional.
const tone = computed(() => hubCardTones.ink)

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

/* ---- Icon chip ---- */
/* Glossy top highlight so the solid ink chip reads as a polished object. */
.tile-sheen {
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0) 60%);
}

:global(.dark) .tile-sheen {
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0) 60%);
}

/* Chip lifts subtly with the card on hover. */
.crisp-card:hover .card-tile {
  transform: scale(1.06);
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
  .building-bar,
  .animate-ping {
    animation: none;
  }

  /* No hover lift for users who prefer reduced motion */
  .crisp-card:hover {
    transform: none;
  }

  .crisp-card:hover .card-tile {
    transform: none;
  }
}
</style>
