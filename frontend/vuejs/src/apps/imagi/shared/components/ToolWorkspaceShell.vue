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
  <div class="spotlight">
  <DefaultLayout>
    <div class="editorial relative min-h-screen">
      <main class="relative">
        <section class="relative isolate overflow-hidden pt-24 sm:pt-28 pb-20 md:pb-24">
          <!-- A low pool of light over the header only — the tool's own content
               below is dense and wants an even floor. (`!` beats .sl-spot's inset.) -->
          <div class="sl-spot h-[560px] !bottom-auto opacity-80" aria-hidden="true"></div>
          <!-- A touch wider than the editorial 68rem measure: these pages carry
               tables and four-across stat rows, not prose. -->
          <div class="mx-auto max-w-6xl px-6 sm:px-8">

            <!-- Back link: the one step back up the hierarchy — the hub's, verbatim -->
            <router-link
              :to="{ name: 'project-hub', params: { projectName } }"
              class="group/back inline-flex items-center gap-2 text-[0.7rem] font-semibold uppercase tracking-[0.16em]
                text-ed-ink-40 transition-[color] duration-[180ms] ease-[ease] hover:text-ed-ink
                focus-visible:!outline-ed-accent"
            >
              <svg
                class="h-[0.9rem] w-[0.9rem] transition-transform duration-[180ms] ease-[ease]
                  group-hover/back:translate-x-[-3px] motion-reduce:group-hover/back:transform-none"
                viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M19 12H5M11 18l-6-6 6-6" />
              </svg>
              <span>Project workspace</span>
            </router-link>

            <!-- Loading -->
            <p v-if="isLoading" class="mt-20 flex items-center gap-[0.7rem] text-[0.9375rem] text-ed-ink-55">
              <span
                class="spinner h-4 w-4 flex-none rounded-[999px] border-[1.5px] border-ed-accent border-t-transparent"
                aria-hidden="true"
              ></span>
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
                  <div class="mt-6 flex items-center gap-4">
                    <h1 class="display text-[2.5rem] sm:text-5xl md:text-[3.4rem]">{{ title }}</h1>
                    <StatusBadge v-if="beta" tone="neutral" label="Beta" />
                  </div>
                </div>
                <p class="lede mt-6 md:mt-0 md:max-w-md md:pb-2 text-base sm:text-[1.0625rem]">
                  {{ description }}
                </p>
              </header>

              <!-- Connect banner: an aside, not an alarm — a hairline panel
                   with the accent diamond, like the editorial callout. -->
              <div
                v-if="showBanner"
                class="rise-item banner mt-10 flex flex-col gap-4 rounded-2xl border border-ed-rule bg-ed-paper-raised
                  px-5 py-[1.1rem] text-[0.9375rem] leading-[1.55] text-ed-ink-70 sm:flex-row sm:items-center sm:gap-[1.1rem]"
                style="animation-delay: 60ms"
              >
                <span class="ml-1 hidden h-[0.4rem] w-[0.4rem] flex-none [transform:rotate(45deg)] bg-ed-accent sm:block" aria-hidden="true"></span>
                <div class="min-w-0 flex-1">
                  <slot name="banner"></slot>
                </div>
                <div class="shrink-0">
                  <slot name="banner-action"></slot>
                </div>
              </div>

              <!-- Tabs: a hairline strip; the active tab is underlined in ink,
                   like the rules everywhere else on the surface. -->
              <nav
                class="rise-item tabs mb-8 mt-11 flex items-center gap-1 overflow-x-auto border-b border-b-ed-rule [scrollbar-width:none]"
                style="animation-delay: 90ms"
                :aria-label="`${title} sections`"
              >
                <router-link
                  v-for="tab in tabs"
                  :key="tab.name"
                  :to="{ name: tab.name, params: { projectName } }"
                  class="focus-ring-inset mb-[-1px] inline-flex items-center gap-2 whitespace-nowrap border-b-[1.5px] px-[0.9rem] py-3
                    text-[0.875rem] font-medium [transition:color_0.18s_ease,border-color_0.18s_ease] first:pl-[0.15rem]"
                  :class="isActiveTab(tab) ? 'tab--active border-b-ed-ink text-ed-ink' : 'border-b-transparent text-ed-ink-55 hover:text-ed-ink'"
                  :aria-current="isActiveTab(tab) ? 'page' : undefined"
                >
                  <i
                    :class="['fas', tab.icon, isActiveTab(tab) ? 'text-ed-accent opacity-100' : 'opacity-[0.55]']"
                    class="text-[0.7rem]"
                    aria-hidden="true"
                  ></i>
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
import { StatusBadge } from '@/shared/components'

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
  /** Still in development: a Beta pill beside the title. */
  beta?: boolean
}>()

const route = useRoute()

function isActiveTab(tab: ToolTab): boolean {
  const current = String(route.name ?? '')
  return current === tab.name || Boolean(tab.children?.includes(current))
}
</script>

<style scoped>
/* The loading spinner's turn: keyframes stay in CSS (scoped names are hashed). */
.spinner {
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* The tab strip scrolls sideways on a phone without showing a scrollbar. */
.tabs::-webkit-scrollbar {
  display: none;
}

@media (prefers-reduced-motion: reduce) {
  .spinner {
    animation: none;
  }
}
</style>
