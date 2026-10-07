<!--
  ToolWorkspaceShell.vue — the frame Sell, Market and Operate all sit in.

  The three workspaces were three copies of the same template (back link,
  loading and not-found states, an icon-tile header, a connect banner and a tab
  strip) that had drifted apart in small ways. They now share this one, and it
  wears the Spotlight stage the project hub and the home page wear: a soft
  light over the header, a Bricolage headline with the lede set opposite it,
  hairline rules. Crossing from the hub into a tool no longer changes typeface,
  floor or light. (The editorial markup is re-lit by the bridge in
  shared/styles/spotlight.css.)

  The tool's own content (cards, tables, forms) renders in the default slot,
  and still uses the denser app vocabulary from shared/styles/ui.ts.
-->
<template>
  <div class="spotlight tool-root">
  <DefaultLayout>
    <div class="editorial tool-page relative min-h-screen">
      <main class="relative">
        <section class="relative isolate overflow-hidden pt-24 sm:pt-28 pb-20 md:pb-24">
          <div class="sl-spot tool-spot" aria-hidden="true"></div>
          <div class="tool-shell">

            <!-- Back link -->
            <router-link :to="{ name: 'project-hub', params: { projectName } }" class="back">
              <svg class="back__arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M19 12H5M11 18l-6-6 6-6" />
              </svg>
              <span>Project workspace</span>
            </router-link>

            <!-- Loading -->
            <p v-if="isLoading" class="state">
              <span class="spinner" aria-hidden="true"></span>
              <span>{{ loadingLabel }}</span>
            </p>

            <!-- Not found -->
            <div v-else-if="!project" class="mt-16 max-w-xl">
              <p class="eyebrow">
                <span class="eyebrow__mark" aria-hidden="true"></span>
                <span class="eyebrow__rule" aria-hidden="true"></span>
                <span>Not found</span>
              </p>
              <h1 class="display mt-6 text-4xl sm:text-5xl">Project not found</h1>
              <p class="lede mt-6 text-lg">We couldn't find this project. It may have been deleted.</p>
              <router-link :to="{ name: 'projects' }" class="btn-outline mt-9">
                Back to projects
              </router-link>
            </div>

            <template v-else>
              <!-- Header: the hub's pattern — eyebrow and headline on the left,
                   the lede set opposite and bottom-aligned with it. -->
              <header class="rise-item mt-10 md:mt-12 md:flex md:items-end md:justify-between gap-12 lg:gap-16">
                <div class="min-w-0">
                  <p class="eyebrow">
                    <span class="eyebrow__rule" aria-hidden="true"></span>
                    <span class="truncate">{{ project.name }}</span>
                  </p>
                  <h1 class="display mt-6 text-[2.5rem] sm:text-5xl md:text-[3.4rem]">{{ title }}</h1>
                </div>
                <p class="lede mt-6 md:mt-0 md:max-w-md md:pb-2 text-base sm:text-[1.0625rem]">
                  {{ description }}
                </p>
              </header>

              <!-- Connect banner: an aside, not an alarm — a hairline panel
                   with the accent diamond, like the editorial callout. -->
              <div v-if="showBanner" class="rise-item banner" style="animation-delay: 60ms">
                <span class="banner__mark" aria-hidden="true"></span>
                <div class="banner__body">
                  <slot name="banner"></slot>
                </div>
                <div class="shrink-0">
                  <slot name="banner-action"></slot>
                </div>
              </div>

              <!-- Tabs -->
              <nav class="rise-item tabs" style="animation-delay: 90ms" :aria-label="`${title} sections`">
                <router-link
                  v-for="tab in tabs"
                  :key="tab.name"
                  :to="{ name: tab.name, params: { projectName } }"
                  class="tab focus-ring-inset"
                  :class="{ 'tab--active': isActiveTab(tab) }"
                  :aria-current="isActiveTab(tab) ? 'page' : undefined"
                >
                  <i :class="['fas', tab.icon]" class="tab__icon" aria-hidden="true"></i>
                  {{ tab.label }}
                </router-link>
              </nav>

              <!-- Active tab -->
              <div class="rise-item crisp-text" style="animation-delay: 140ms">
                <slot></slot>
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
import { useRoute } from 'vue-router'
import { DefaultLayout } from '@/shared/layouts'

export interface ToolTab {
  name: string
  label: string
  icon: string
  /** Child routes that should keep this tab lit (a campaign's detail page). */
  children?: string[]
}

defineProps<{
  projectName: string
  project: { name: string } | null | undefined
  isLoading: boolean
  title: string
  description: string
  loadingLabel: string
  tabs: ToolTab[]
  showBanner?: boolean
}>()

const route = useRoute()

function isActiveTab(tab: ToolTab): boolean {
  const current = String(route.name ?? '')
  return current === tab.name || Boolean(tab.children?.includes(current))
}
</script>

<style scoped>
/* A low pool of light over the header only — the tool's own content below
   is dense and wants an even floor. */
.tool-page .tool-spot {
  height: 560px;
  bottom: auto;
  opacity: 0.8;
}

/* A touch wider than the editorial 68rem measure: these pages carry tables
   and four-across stat rows, not prose. */
.tool-shell {
  max-width: 72rem;
  margin: 0 auto;
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}

@media (min-width: 640px) {
  .tool-shell {
    padding-left: 2rem;
    padding-right: 2rem;
  }
}

/* The one step back up the hierarchy — the hub's back link, verbatim. */
.back {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--ink-40);
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

.banner {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 2.5rem;
  padding: 1.1rem 1.25rem;
  border: 1px solid var(--rule);
  border-radius: 1rem;
  background: var(--paper-raised);
  font-size: 0.9375rem;
  line-height: 1.55;
  color: var(--ink-70);
}

@media (min-width: 640px) {
  .banner {
    flex-direction: row;
    align-items: center;
    gap: 1.1rem;
  }
}

.banner__mark {
  display: none;
  flex: none;
  width: 0.4rem;
  height: 0.4rem;
  margin-left: 0.25rem;
  transform: rotate(45deg);
  background: var(--accent);
}

@media (min-width: 640px) {
  .banner__mark {
    display: block;
  }
}

.banner__body {
  flex: 1;
  min-width: 0;
}

/* Hairline tab strip; the active tab is underlined in ink, like the rules
   everywhere else on the surface. */
.tabs {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-top: 2.75rem;
  margin-bottom: 2rem;
  overflow-x: auto;
  border-bottom: 1px solid var(--rule);
  scrollbar-width: none;
}

.tabs::-webkit-scrollbar {
  display: none;
}

.tab {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 0.9rem;
  margin-bottom: -1px;
  border-bottom: 1.5px solid transparent;
  white-space: nowrap;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink-55);
  transition: color 0.18s ease, border-color 0.18s ease;
}

.tab:first-child {
  padding-left: 0.15rem;
}

.tab:hover {
  color: var(--ink);
}

.tab--active {
  color: var(--ink);
  border-bottom-color: var(--ink);
}

.tab__icon {
  font-size: 0.7rem;
  opacity: 0.55;
}

.tab--active .tab__icon {
  color: var(--accent);
  opacity: 1;
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
