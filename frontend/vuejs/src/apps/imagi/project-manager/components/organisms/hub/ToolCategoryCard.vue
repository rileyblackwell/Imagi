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
  <component
    :is="isBuildLocked ? 'div' : 'router-link'"
    :to="isBuildLocked ? undefined : target"
    class="sl-card module"
    :class="[`module--${layout}`, { 'module--building': isBuildLocked }]"
    :title="isBuildLocked ? 'Imagi is building your app — this module unlocks the moment the build finishes' : tool.name"
    :aria-disabled="isBuildLocked ? 'true' : undefined"
  >
    <!-- ==================== FEATURE (Build) ==================== -->
    <template v-if="layout === 'feature'">
      <div class="module__head">
        <span class="sl-card__icon module__icon"><LineIcon :name="tool.lineIcon" /></span>
        <div>
          <h3 class="sl-card__title">{{ tool.name }}</h3>
          <p class="sl-card__body">{{ isBuildLocked ? 'Imagi is writing your first version' : tool.tagline }}</p>
        </div>
      </div>

      <!-- A sketch of the workspace: the conversation on the left, the page it
           is writing on the right. Decoration only. -->
      <div class="module__window" aria-hidden="true">
        <div class="module__chrome"><i></i><i></i><i></i></div>
        <div class="module__sketch">
          <div class="module__chat">
            <span></span><span class="is-you"></span><span></span><span class="is-short"></span><span class="is-you"></span>
          </div>
          <div class="module__page"><span class="module__page-bar"></span></div>
        </div>
      </div>

      <div class="module__foot">
        <template v-if="isBuildLocked">
          <!-- The accent sweeping along a hairline reports the work in progress. -->
          <div class="module__track" aria-hidden="true"><span class="module__bar"></span></div>
          <p class="module__cta--waiting">Building</p>
        </template>
        <template v-else>
          <ul class="module__features module__chips">
            <li v-for="feature in tool.features" :key="feature.name">{{ feature.name }}</li>
          </ul>
          <span class="module__open">
            Open workspace
            <svg class="module__arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M5 12h14M13 6l6 6-6 6" />
            </svg>
          </span>
        </template>
      </div>
    </template>

    <!-- ==================== ROW (Run tools) ==================== -->
    <template v-else>
      <span class="sl-card__icon module__icon"><LineIcon :name="tool.lineIcon" /></span>
      <div class="module__text">
        <div class="module__title">
          <h3 class="sl-card__title">{{ tool.name }}</h3>
          <StatusBadge v-if="tool.beta" tone="neutral" label="Beta" />
        </div>
        <p class="sl-card__body">{{ tool.tagline }}</p>
        <p v-if="isBuildLocked" class="module__cta--waiting">Building</p>
        <ul v-else class="module__features module__inline">
          <li v-for="feature in tool.features" :key="feature.name">{{ feature.name }}</li>
        </ul>
      </div>
      <span class="module__go" aria-hidden="true">
        <svg class="module__arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M5 12h14M13 6l6 6-6 6" />
        </svg>
      </span>
    </template>
  </component>
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
/* The card is a link, so it carries the states. The lift comes from .sl-card;
   the warm border and glow on hover are the module's own. */
.module {
  color: var(--sl-text);
  text-decoration: none;
}

.module:focus-visible {
  outline: 2px solid var(--sl-focus);
  outline-offset: 4px;
}

.spotlight .module:hover {
  border-color: var(--sl-warm-line);
  box-shadow: var(--sl-card-shadow), 0 24px 50px -30px var(--sl-glow);
}

.module__icon {
  flex: none;
  transition: transform 0.25s var(--app-ease), border-color 0.25s ease;
}

.spotlight .module .module__icon {
  margin-bottom: 0;
}

.module__icon :deep(svg) {
  width: 22px;
  height: 22px;
}

.module:hover .module__icon {
  transform: translateY(-2px);
  border-color: var(--sl-warm-line);
}

.module__arrow {
  width: 1rem;
  height: 1rem;
  transition: transform 0.18s ease;
}

.module:hover .module__arrow {
  transform: translateX(3px);
}

/* --- Feature (Build) -----------------------------------------------------
   The lit half: a gradient hairline round the edge and a warm pool beneath. */

.spotlight .module--feature {
  position: relative;
  gap: 0;
  height: 100%;
  padding: 30px;
  border-radius: 24px;
  border-color: transparent;
  box-shadow: var(--sl-card-shadow), 0 40px 90px -50px var(--sl-glow);
}

.module--feature::before {
  content: '';
  position: absolute;
  inset: -1px;
  padding: 1px;
  border-radius: inherit;
  background: var(--sl-prompt-edge);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.spotlight .module--feature:hover {
  border-color: transparent;
  box-shadow: var(--sl-card-shadow), 0 40px 90px -40px var(--sl-glow);
}

.module__head {
  display: flex;
  align-items: center;
  gap: 16px;
}

.spotlight .module--feature .sl-card__title {
  font-size: clamp(28px, 3vw, 36px);
  letter-spacing: -0.03em;
  line-height: 1.05;
}

.spotlight .module--feature .sl-card__body {
  margin-top: 4px;
  font-size: 16px;
}

.module__window {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 200px;
  margin: 26px 0 24px;
  overflow: hidden;
  border: 1px solid var(--sl-line-strong);
  border-radius: 14px;
  background: var(--sl-bg-deep);
}

.module__chrome {
  display: flex;
  gap: 6px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--sl-line);
  background: var(--sl-chrome-bg);
}

.module__chrome i {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--sl-chrome-dot);
}

.module__sketch {
  flex: 1;
  display: grid;
  grid-template-columns: 38% 1fr;
  gap: 12px;
  padding: 14px;
}

.module__chat {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.module__chat span,
.module__page {
  border: 1px solid var(--sl-line);
  border-radius: 8px;
  background: var(--sl-chip-bg);
}

.module__chat span {
  height: 22px;
}

.module__chat .is-you {
  align-self: flex-end;
  width: 70%;
  border-color: var(--sl-warm-line);
}

.module__chat .is-short {
  width: 60%;
}

.module__page {
  position: relative;
  background: linear-gradient(180deg, var(--sl-chip-bg), transparent);
}

.module__page-bar {
  position: absolute;
  top: 18px;
  left: 14px;
  right: 40%;
  height: 10px;
  border-radius: 4px;
  background: var(--sl-grad);
  opacity: 0.5;
}

.module__foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.module__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.module__chips li {
  padding: 5px 11px;
  border: 1px solid var(--sl-line);
  border-radius: 999px;
  background: var(--sl-chip-bg);
  font-size: 12.5px;
  color: var(--sl-muted);
}

/* The page's one gradient button. The whole card is the link, so this is a
   span dressed as the button rather than a second, nested control. */
.module__open {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 11px 20px;
  border-radius: 999px;
  background: var(--sl-grad);
  color: var(--sl-on-accent);
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: var(--sl-btn-shadow);
  transition: box-shadow 0.2s ease;
}

.module--feature:hover .module__open {
  box-shadow: var(--sl-btn-shadow-hover);
}

/* --- Row (Run tools) ---------------------------------------------------- */

.spotlight .module--row {
  flex: 1;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 18px;
  padding: 22px;
}

.module__title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.module__text {
  min-width: 0;
}

.spotlight .module--row .sl-card__body {
  margin-top: 1px;
  font-size: 14px;
}

.module__inline {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 18px;
  margin: 10px 0 0;
  padding: 0;
  list-style: none;
  font-size: 13px;
  color: var(--sl-muted);
}

.module__inline li {
  display: inline-flex;
  align-items: center;
  gap: 7px;
}

.module__inline li::before {
  content: '';
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--sl-grad);
}

.module__go {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border: 1px solid var(--sl-line-strong);
  border-radius: 999px;
  color: var(--sl-faint);
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.module--row:hover .module__go {
  border-color: transparent;
  background: var(--sl-grad);
  color: var(--sl-on-accent);
}

/* --- Building ------------------------------------------------------------
   The one module that can be busy. It keeps the card's shape and swaps the
   capabilities and button for the reason it can't be opened yet. */

.module--building {
  cursor: progress;
}

.spotlight .module--building:hover {
  transform: none;
}

.module--building .module__icon {
  animation: module-pulse 2.4s ease-in-out infinite;
}

.module__foot .module__track {
  flex: 1 1 100%;
}

.module__track {
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

.module__cta--waiting {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
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

@media (max-width: 560px) {
  .spotlight .module--feature {
    padding: 22px;
  }

  .module__window {
    min-height: 160px;
  }

  .spotlight .module--row {
    gap: 14px;
    padding: 18px;
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
