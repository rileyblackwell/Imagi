<!--
  ToolCategoryCard.vue — one module on the project hub.

  Renders a BusinessTool (Build / Sell / Market / Operate) as a Spotlight card,
  in one of the two shapes the hub's "two halves" layout uses:

    - feature: the Build half. A tall, lit-edged panel with a sketch of the
      workspace (chat beside a page) and the one gradient button on the page.
    - row:     a Run tool. A compact row — mark, name, tagline, capabilities
      inline — with a round arrow that takes the light on hover.

  The same mark, title, tagline and capabilities the home page uses describe
  each module, and the tool's own accent is deliberately left out: the stage
  has one light, and four differently-coloured cards would read as decoration
  rather than as navigation.
-->
<template>
  <router-link
    :to="target"
    class="sl-card module group text-sl-text no-underline focus-visible:!outline-offset-4"
    :class="[
      `module--${layout}`,
      { 'module--building': isBuilding },
      layout === 'feature'
        ? `relative h-full !gap-0 !rounded-[24px] !border-transparent !p-[30px] ![box-shadow:var(--sl-card-shadow),0_40px_90px_-50px_var(--sl-glow)]
           hover:!border-transparent hover:![box-shadow:var(--sl-card-shadow),0_40px_90px_-40px_var(--sl-glow)] max-[560px]:!p-[22px]
           before:pointer-events-none before:absolute before:-inset-px before:rounded-[inherit] before:bg-sl-prompt-edge before:p-px before:content-['']
           before:[-webkit-mask:linear-gradient(#000_0_0)_content-box,linear-gradient(#000_0_0)] before:[mask-composite:exclude]`
        : `!grid flex-1 grid-cols-[auto_minmax(0,1fr)_auto] items-center !gap-[18px] !p-[22px] max-[560px]:!gap-[14px] max-[560px]:!p-[18px]
           hover:!border-sl-warm-line hover:![box-shadow:var(--sl-card-shadow),0_24px_50px_-30px_var(--sl-glow)]`,
    ]"
    :title="isBuilding ? 'Imagi is building your app. Open the workspace to watch it.' : tool.name"
  >
    <!-- The card is a link, so it carries the states. The lift comes from
         .sl-card; the warm border and glow on hover are the module's own, so
         they (and the layout's overrides of .sl-card) are marked important. -->

    <!-- ==================== FEATURE (Build) ==================== -->
    <!-- The lit half: a gradient hairline round the edge (::before) and a warm
         pool beneath. -->
    <template v-if="layout === 'feature'">
      <div class="flex items-center gap-4">
        <span :class="ICON" class="module__icon"><LineIcon :name="tool.lineIcon" /></span>
        <div>
          <h3 class="sl-card__title !text-[clamp(28px,3vw,36px)] !leading-[1.05] !tracking-[-0.03em]">{{ tool.name }}</h3>
          <p class="sl-card__body !mt-[4px] !text-[16px]">{{ isBuilding ? 'Imagi is writing your first version' : tool.tagline }}</p>
        </div>
      </div>

      <!-- A sketch of the workspace: the conversation on the left, the page it
           is writing on the right. Decoration only. -->
      <div
        class="module__window mx-0 mb-[24px] mt-[26px] flex min-h-[200px] flex-1 flex-col overflow-hidden rounded-[14px] border border-sl-line-strong bg-sl-bg-deep max-[560px]:min-h-[160px]"
        aria-hidden="true"
      >
        <div class="flex gap-[6px] border-b border-b-sl-line bg-sl-chrome-bg px-[12px] py-[10px]">
          <i class="h-[9px] w-[9px] rounded-[50%] bg-sl-chrome-dot"></i>
          <i class="h-[9px] w-[9px] rounded-[50%] bg-sl-chrome-dot"></i>
          <i class="h-[9px] w-[9px] rounded-[50%] bg-sl-chrome-dot"></i>
        </div>
        <div class="grid flex-1 grid-cols-[38%_1fr] gap-[12px] p-[14px]">
          <div class="flex flex-col gap-[8px]">
            <span class="h-[22px] rounded-[8px] border border-sl-line bg-sl-chip-bg"></span>
            <span class="h-[22px] w-[70%] self-end rounded-[8px] border border-sl-warm-line bg-sl-chip-bg"></span>
            <span class="h-[22px] rounded-[8px] border border-sl-line bg-sl-chip-bg"></span>
            <span class="h-[22px] w-[60%] rounded-[8px] border border-sl-line bg-sl-chip-bg"></span>
            <span class="h-[22px] w-[70%] self-end rounded-[8px] border border-sl-warm-line bg-sl-chip-bg"></span>
          </div>
          <div class="relative rounded-[8px] border border-sl-line bg-[image:linear-gradient(180deg,var(--sl-chip-bg),transparent)]">
            <span class="absolute left-[14px] right-[40%] top-[18px] h-[10px] rounded-[4px] bg-sl-grad opacity-50"></span>
          </div>
        </div>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-4">
        <template v-if="isBuilding">
          <!-- The accent sweeping along a hairline reports the work in progress. -->
          <div class="module__track h-[2px] flex-[1_1_100%] overflow-hidden rounded-[2px] bg-sl-line" aria-hidden="true">
            <span class="module__bar block h-full w-[40%] bg-sl-grad"></span>
          </div>
          <p :class="WAITING">Building</p>
        </template>
        <template v-else>
          <ul class="module__features module__chips m-0 flex list-none flex-wrap gap-[6px] p-0">
            <li
              v-for="feature in tool.features"
              :key="feature.name"
              class="rounded-[999px] border border-sl-line bg-sl-chip-bg px-[11px] py-[5px] text-[12.5px] text-sl-muted"
            >{{ feature.name }}</li>
          </ul>
          <!-- The page's one gradient button. The whole card is the link, so
               this is a span dressed as the button rather than a second,
               nested control. -->
          <span
            class="module__open inline-flex items-center gap-2 whitespace-nowrap rounded-[999px] bg-sl-grad px-[20px] py-[11px] text-[14px] font-semibold text-sl-on-accent
              shadow-sl-btn [transition:box-shadow_0.2s_ease] group-hover:shadow-sl-btn-hover"
          >
            Open workspace
            <svg :class="ARROW" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M5 12h14M13 6l6 6-6 6" />
            </svg>
          </span>
        </template>
      </div>
    </template>

    <!-- ==================== ROW (Run tools) ==================== -->
    <template v-else>
      <span :class="ICON" class="module__icon"><LineIcon :name="tool.lineIcon" /></span>
      <div class="min-w-0">
        <div class="flex items-center gap-[10px]">
          <h3 class="sl-card__title">{{ tool.name }}</h3>
          <StatusBadge v-if="tool.beta" tone="neutral" label="Beta" />
        </div>
        <p class="sl-card__body !mt-px !text-[14px]">{{ tool.tagline }}</p>
        <p v-if="isBuilding" :class="WAITING">Building</p>
        <ul v-else class="module__features mx-0 mb-0 mt-[10px] flex list-none flex-wrap gap-x-[18px] gap-y-[4px] p-0 text-[13px] text-sl-muted">
          <li
            v-for="feature in tool.features"
            :key="feature.name"
            class="inline-flex items-center gap-[7px] before:h-[5px] before:w-[5px] before:rounded-[50%] before:bg-sl-grad before:content-['']"
          >{{ feature.name }}</li>
        </ul>
      </div>
      <span
        class="grid h-[38px] w-[38px] place-items-center rounded-[999px] border border-sl-line-strong text-sl-faint
          [transition:background_0.2s_ease,color_0.2s_ease,border-color_0.2s_ease] group-hover:border-transparent group-hover:bg-sl-grad group-hover:text-sl-on-accent"
        aria-hidden="true"
      >
        <svg :class="ARROW" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M5 12h14M13 6l6 6-6 6" />
        </svg>
      </span>
    </template>
  </router-link>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { RouteLocationRaw } from 'vue-router'
import { type BusinessTool } from '../../../utils/businessTools'
import { LineIcon, StatusBadge } from '@/shared/components'

const props = withDefaults(
  defineProps<{
    tool: BusinessTool
    projectSlug: string
    /** The project's generation_status; drives the Build module's "AI building" state. */
    buildStatus?: 'pending' | 'generating' | 'completed' | 'failed' | null
    /** 'feature' for the Build half of the hub, 'row' for each Run tool. */
    layout?: 'feature' | 'row'
  }>(),
  { layout: 'row', buildStatus: null }
)

// The module's mark: .sl-card__icon, lifted and warmed on hover, with a
// larger glyph. The pulse while building is in <style>.
const ICON =
  'sl-card__icon flex-none !mb-0 [transition:transform_0.25s_var(--app-ease),border-color_0.25s_ease] group-hover:-translate-y-[2px] group-hover:!border-sl-warm-line motion-reduce:group-hover:transform-none'
const ARROW = 'h-4 w-4 [transition:transform_0.18s_ease] group-hover:translate-x-[3px] motion-reduce:group-hover:transform-none'
// "Building", lit by the gradient.
const WAITING = 'module__cta--waiting m-0 bg-sl-grad bg-clip-text text-[0.78rem] font-semibold uppercase tracking-[0.14em] text-transparent'

/**
 * The initial AI build is still running. The Build module says so, and still
 * opens: the workspace shows the home page being written and the app the
 * moment it lands. Only Build has this state.
 *
 * Strictly 'generating', the status the backend sets synchronously the moment
 * a build starts. 'pending' is the transient/legacy default.
 */
const isBuilding = computed(
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
/* The building state's motion. Keyframes stay CSS: scoped keyframe names are
   hashed, so a utility can't reference them. */
.module--building .module__icon {
  animation: module-pulse 2.4s ease-in-out infinite;
}

.module__bar {
  animation: module-sweep 1.8s ease-in-out infinite;
}

@keyframes module-sweep {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(250%);
  }
}

@keyframes module-pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

@media (prefers-reduced-motion: reduce) {
  .module__bar,
  .module--building .module__icon {
    animation: none;
  }
}
</style>
