<!--
  ToolCategoryCard.vue - A single workspace category on the project hub.

  Renders one BusinessTool (Build / Sell / Market / Operate) as a card that
  links either to the app builder or to the generic coming-soon tool page.
-->
<template>
  <router-link
    :to="target"
    class="crisp-card group relative flex flex-col h-full p-6 rounded-2xl bg-white dark:bg-white/[0.05] border transition-colors duration-300"
    :class="accent.cardBorder"
    :title="tool.name"
  >
    <!-- Soft accent glow on hover -->
    <div
      class="pointer-events-none absolute -top-px -right-px w-40 h-40 rounded-full blur-3xl opacity-0 group-hover:opacity-100 bg-gradient-to-br to-transparent transition-opacity duration-500"
      :class="accent.glow"
    ></div>

    <!-- Icon + status -->
    <div class="relative flex items-start justify-between mb-4">
      <div
        class="w-12 h-12 rounded-xl flex items-center justify-center border transition-colors duration-300"
        :class="[accent.iconWrap]"
      >
        <i :class="['fas', tool.icon, accent.iconText]" class="text-xl"></i>
      </div>
      <span
        v-if="isBuilding"
        class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[11px] font-semibold uppercase tracking-[0.14em] transition-colors duration-300"
        :class="accent.badge"
      >
        <span class="w-3 h-3 rounded-full border-2 border-current border-t-transparent animate-spin"></span>
        AI building
      </span>
      <span
        v-else-if="tool.status !== 'available'"
        class="inline-flex items-center px-2.5 py-1 rounded-full border border-blue-950/10 dark:border-white/15 bg-blue-950/[0.03] dark:bg-white/[0.04] text-[11px] font-semibold uppercase tracking-[0.14em] text-blue-950/50 dark:text-white/50 transition-colors duration-300"
      >
        Coming soon
      </span>
    </div>

    <!-- Name + tagline -->
    <div class="relative flex-1">
      <h3 class="text-lg font-semibold text-blue-950 dark:text-white mb-1 transition-colors duration-300">
        {{ tool.name }}
      </h3>
      <p class="text-sm text-blue-950/70 dark:text-blue-100/70 leading-snug transition-colors duration-300">
        {{ isBuilding ? 'Imagi is building the first version of your app from your business description…' : tool.tagline }}
      </p>
    </div>

    <!-- CTA -->
    <div
      class="relative flex items-center gap-1.5 text-sm font-medium mt-5 pt-4 border-t border-blue-200/60 dark:border-white/[0.1] transition-colors duration-300"
      :class="accent.link"
    >
      <span>{{ tool.status === 'available' ? 'Open workspace' : 'Preview' }}</span>
      <i class="fas fa-arrow-right text-xs group-hover:translate-x-1 transition-transform duration-200"></i>
    </div>
  </router-link>
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

const isBuilding = computed(() => props.tool.id === 'build' && props.buildStatus === 'generating')

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

:global(.dark) .crisp-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}
</style>
