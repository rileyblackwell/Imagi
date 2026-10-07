<!--
  ToolCategoryCard.vue — one module on the project hub.

  Renders a BusinessTool (Build / Sell / Market / Operate) as a Spotlight card:
  the same mark, title, body and highlights the home page uses to describe the
  same four modules, with the tool's own accent deliberately left out. The
  stage has one light, and four differently-coloured cards on one page would
  read as decoration rather than as navigation.
-->
<template>
  <component
    :is="isBuildLocked ? 'div' : 'router-link'"
    :to="isBuildLocked ? undefined : target"
    class="sl-card module"
    :class="{ 'module--building': isBuildLocked }"
    :title="isBuildLocked ? 'Imagi is building your app — this module unlocks the moment the build finishes' : tool.name"
    :aria-disabled="isBuildLocked ? 'true' : undefined"
  >
    <span class="sl-card__icon module__icon"><LineIcon :name="tool.lineIcon" /></span>
    <h3 class="sl-card__title">{{ tool.name }}</h3>

    <!-- ==================== BUILDING STATE ==================== -->
    <template v-if="isBuildLocked">
      <p class="sl-card__body">
        Imagi is turning your business description into a tailored first version. This
        usually takes a moment.
      </p>

      <!--
        The rule that opens the foot line, with the accent sweeping along it —
        so the module's own hairline is what reports the work, rather than a
        progress bar parked above one.
      -->
      <div class="module__track" aria-hidden="true">
        <span class="module__bar"></span>
      </div>

      <p class="module__cta module__cta--waiting">Building</p>
    </template>

    <!-- ==================== DEFAULT STATE ==================== -->
    <template v-else>
      <p class="sl-card__body">{{ tool.tagline }}</p>

      <ul class="sl-highlights module__features">
        <li v-for="feature in tool.features" :key="feature.name">{{ feature.name }}</li>
      </ul>

      <p class="module__cta">
        <span>Open</span>
        <svg class="module__arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M5 12h14M13 6l6 6-6 6" />
        </svg>
      </p>
    </template>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { RouteLocationRaw } from 'vue-router'
import { type BusinessTool } from '../../../utils/businessTools'
import { LineIcon } from '@/shared/components'

const props = defineProps<{
  tool: BusinessTool
  projectSlug: string
  /** The project's generation_status; drives the Build module's "AI building" state. */
  buildStatus?: 'pending' | 'generating' | 'completed' | 'failed' | null
}>()

/**
 * The initial AI build is still running. While it is, the Build module is
 * locked: it shows a dedicated building state and cannot navigate into the
 * workspace, so users never enter a half-built project. Only Build is gated.
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
/* The card is a link, so it carries the states: the "Open" line at its foot
   resolves from muted to full text and the arrow takes the light. The lift and
   border come from .sl-card. */
.module {
  color: var(--sl-text);
  text-decoration: none;
}

.module:focus-visible {
  outline: 2px solid var(--sl-focus);
  outline-offset: 4px;
}

/* The card's own highlights pin to its foot with an auto margin; here the CTA
   below owns it instead, so the four "Open" lines land on one baseline however
   many capabilities each module lists. */
.module .module__features {
  margin: 8px 0 22px;
}

.module__icon :deep(svg) {
  width: 22px;
  height: 22px;
}

.module__cta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: auto 0 0;
  padding-top: 1rem;
  border-top: 1px solid var(--sl-line);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-faint);
  transition: color 0.18s ease;
}

.module:hover .module__cta {
  color: var(--sl-text);
}

.module:hover .module__arrow {
  color: var(--sl-coral);
}

.module:hover {
  box-shadow: var(--sl-card-shadow), 0 24px 50px -30px var(--sl-glow);
}

.module .module__icon {
  transition: transform 0.25s var(--app-ease), border-color 0.25s ease;
}

.module:hover .module__icon {
  transform: translateY(-2px);
  border-color: var(--sl-warm-line);
}

.module__arrow {
  width: 0.95rem;
  height: 0.95rem;
  margin-left: auto;
  transition: transform 0.18s ease;
}

.module:hover .module__arrow {
  transform: translateX(3px);
}

/* --- Building ------------------------------------------------------------
   The one module that can be busy. It keeps the card's shape and swaps the
   capability list for the reason it can't be opened yet. */

.module--building {
  cursor: progress;
}

.spotlight .module--building:hover {
  transform: none;
}

.module--building .module__icon {
  animation: module-pulse 2.4s ease-in-out infinite;
}

.module__track {
  margin-top: auto;
  height: 2px;
  overflow: hidden;
  border-radius: 2px;
  background: var(--sl-line);
}

.module__bar {
  display: block;
  width: 40%;
  height: 100%;
  background: var(--sl-grad);
  animation: module-sweep 1.8s ease-in-out infinite;
}

/* The track above it is already the rule, so this one drops its own. */
.module__cta--waiting {
  margin-top: 0;
  border-top: 0;
  background: var(--sl-grad);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
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

  .module:hover .module__arrow,
  .module:hover .module__icon {
    transform: none;
  }
}
</style>
