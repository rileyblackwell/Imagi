<!-- Global authenticated app shell: one sidebar engine for every workspace
     (docs, builder, …). The sidebar's surface, motion, collapse behaviour and
     the top-bar toggle are shared here; each section customises width and the
     panel's contents through props + slots.

     Collapsed means GONE: the panel slides fully off-canvas on every
     breakpoint and the content reclaims the full width. The only control that
     brings it back lives in the top bar (SidebarToggle), never inside the
     panel — so it can never disappear along with the thing it opens. -->
<template>
  <BaseLayout>
    <!-- App-shell views (the builder workspace) pin the shell to the dynamic
         viewport height and clip overflow so the document itself can never
         scroll — otherwise the vh/dvh mismatch on mobile leaves a few dozen
         scrollable pixels that slide the content up under the fixed navbar. -->
    <div class="flex" :class="appShell ? 'h-dvh overflow-hidden' : 'min-h-screen'">
      <!-- Sidebar: the same glass as the navbar (bg-white/80 blur + hairline),
           so the top bar and the panel read as one continuous frame around the
           page. On mobile it drops below the navbar and becomes an off-canvas
           drawer that floats over the content. -->
      <aside
        class="sidebar-panel fixed bottom-0 left-0 z-30 flex flex-col max-md:top-16 border-r border-blue-950/[0.08] dark:border-white/[0.08] bg-white/80 dark:bg-[#0a0a0a]/80 backdrop-blur-xl max-md:shadow-[0_24px_60px_-20px_rgba(15,23,42,0.35)] dark:max-md:shadow-[0_24px_60px_-20px_rgba(0,0,0,0.7)]"
        :class="[
          asideWidthClass,
          // The stacked frame drops the panel below the full-width top bar so
          // the bar's toggle + wordmark own the true top-left corner; other
          // sections keep the panel flush to the top on desktop.
          stackedNav ? 'top-16' : 'md:top-0',
          isSidebarCollapsed ? '-translate-x-full pointer-events-none' : 'translate-x-0'
        ]"
        :aria-hidden="isSidebarCollapsed ? 'true' : undefined"
      >
        <!-- Section header (skipped for compact app shells like the builder,
             which supply their own panel header). Holds a section label and
             the in-panel collapse control. -->
        <div
          v-if="!compactTop"
          class="flex-shrink-0 h-14 flex items-center gap-2 px-3 border-b border-blue-950/[0.08] dark:border-white/[0.08]"
        >
          <div class="flex-1 min-w-0">
            <slot name="sidebar-header"></slot>
          </div>
        </div>

        <!-- Navigation (used when a section passes navigationItems directly
             rather than filling the sidebar-content slot). -->
        <nav v-if="navigationItems.length" class="flex-shrink-0 py-4">
          <div class="px-3 space-y-1">
            <router-link
              v-for="item in navigationItems"
              :key="item.name"
              :to="item.to"
              :class="[
                'group flex items-center px-3 py-2 text-sm font-medium rounded-xl transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]',
                isActivePath(item)
                  ? 'nav-item-active text-blue-950 dark:text-white'
                  : 'text-blue-950/65 dark:text-blue-100/65 hover:bg-blue-950/[0.04] dark:hover:bg-white/[0.06] hover:text-blue-950 dark:hover:text-white'
              ]"
            >
              <i
                :class="[
                  item.icon,
                  'text-base w-5 text-center transition-colors duration-200 mr-3',
                  isActivePath(item) ? 'text-blue-700 dark:text-blue-300' : 'text-blue-950/45 dark:text-blue-100/40 group-hover:text-blue-950 dark:group-hover:text-white'
                ]"
              ></i>
              <span class="truncate">{{ item.name }}</span>
            </router-link>
          </div>
        </nav>

        <!-- Custom Sidebar Content -->
        <div class="flex-1 min-h-0 overflow-hidden">
          <slot name="sidebar-content" :isSidebarCollapsed="isSidebarCollapsed" :toggleSidebar="toggleSidebar"></slot>
        </div>

        <!-- Bottom Actions -->
        <div v-if="$slots['sidebar-bottom']" class="flex-shrink-0 border-t border-blue-950/[0.08] dark:border-white/[0.08]">
          <slot name="sidebar-bottom"></slot>
        </div>
      </aside>

      <!-- Main content — margin animates to match the sidebar, and drops to 0
           when the panel is collapsed (or on mobile, where the panel overlays
           rather than pushes). -->
      <div
        class="content-shell flex-1 flex flex-col ml-0"
        :class="[
          appShell ? 'h-full min-h-0 overflow-hidden' : 'min-h-screen',
          isSidebarCollapsed ? '' : contentOffsetClass
        ]"
      >
        <!-- Navbar -->
        <BaseNavbar
          class="navbar-shell fixed top-0 right-0 left-0 z-20 bg-white/80 dark:bg-[#0a0a0a]/80 backdrop-blur-md border-b border-blue-950/[0.08] dark:border-white/[0.08]"
          :class="(isSidebarCollapsed || stackedNav) ? '' : navOffsetClass"
          :fluid="stackedNav"
        >
          <!-- The permanent show/hide control, pinned to the far left of the
               top bar (before the wordmark) so collapsing the panel never
               hides the only way back. -->
          <template #left-leading>
            <SidebarToggle
              :open="!isSidebarCollapsed"
              class="mr-1 -ml-3 sm:-ml-5 lg:-ml-9"
              :class="hideToggleOnMobile ? 'max-md:hidden' : ''"
              @toggle="toggleSidebar"
            />
          </template>
          <template #left>
            <slot
              name="navbar-left"
              :isSidebarCollapsed="isSidebarCollapsed"
              :toggleSidebar="toggleSidebar"
              :setSidebarCollapsed="setSidebarCollapsed"
            ></slot>
          </template>
          <template #center>
            <div class="flex items-center justify-center">
              <slot
                name="navbar-center"
                :isSidebarCollapsed="isSidebarCollapsed"
                :toggleSidebar="toggleSidebar"
                :setSidebarCollapsed="setSidebarCollapsed"
              ></slot>
            </div>
          </template>
          <template #right>
            <div class="flex items-center justify-end">
              <slot
                name="navbar-right"
                :isSidebarCollapsed="isSidebarCollapsed"
                :toggleSidebar="toggleSidebar"
                :setSidebarCollapsed="setSidebarCollapsed"
              ></slot>
            </div>
          </template>
        </BaseNavbar>

        <!-- Main content area -->
        <main
          class="flex-1 flex flex-col relative pt-16 bg-white dark:bg-[#0a0a0a] overflow-hidden"
          :class="appShell ? 'min-h-0' : ''"
        >
          <slot :isSidebarCollapsed="isSidebarCollapsed"></slot>
        </main>

        <!-- Footer (hidden for full-screen app-shell views like the builder);
             BaseFooter supplies its own white / dark #0a0a0a canvas + hairline. -->
        <BaseFooter v-if="!appShell" />
      </div>

      <!-- Mobile scrim: dims the content behind the drawer and taps to close.
           Desktop pushes content instead, so it's mobile-only. -->
      <transition
        enter-active-class="transition-opacity duration-200 ease-out"
        leave-active-class="transition-opacity duration-200 ease-in"
        enter-from-class="opacity-0"
        leave-to-class="opacity-0"
      >
        <div
          v-if="!isSidebarCollapsed"
          class="md:hidden fixed top-16 left-0 right-0 bottom-0 z-20 bg-blue-950/25 dark:bg-black/45 backdrop-blur-[1px]"
          aria-hidden="true"
          @click="setSidebarCollapsed(true)"
        ></div>
      </transition>
    </div>
  </BaseLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/shared/stores/auth'
import BaseLayout from './BaseLayout.vue'
import { BaseNavbar, BaseFooter, SidebarToggle } from '@/shared/components'

interface NavigationItem {
  name: string
  to: string
  icon?: string
  exact?: boolean
  children?: NavigationItem[]
}

const props = withDefaults(defineProps<{
  navigationItems: NavigationItem[]
  storageKey?: string
  compactTop?: boolean
  // When true, this is a full-screen app shell (e.g. the builder workspace):
  // the site footer is dropped so the content fills the viewport exactly.
  appShell?: boolean
  // When true, the top bar spans the full viewport width with its controls
  // (toggle + wordmark) pinned to the true top-left corner, and the sidebar
  // sits *below* the bar rather than beside it — the builder workspace's frame.
  // app shells always use this; other sections (docs) opt in without adopting
  // the footer-drop / viewport-clip behaviour that `appShell` also brings.
  fullWidthNav?: boolean
  // Per-section sizing. Passed as ready-made utility classes so the responsive
  // (md:) variants compose cleanly and there are no scoped-style specificity
  // fights. The content/nav offsets are applied only at md+ — on mobile the
  // panel overlays, so the content is never pushed.
  asideWidthClass?: string
  contentOffsetClass?: string
  navOffsetClass?: string
  // Start collapsed on small screens (no stored preference yet) so a section
  // whose panel is a menu (docs) opens to its content, not the menu.
  mobileDefaultCollapsed?: boolean
  // Sections with their own mobile view switcher (the builder) suppress the
  // top-bar toggle on mobile to avoid two competing controls.
  hideToggleOnMobile?: boolean
  // Deprecated, accepted for back-compat with existing callers.
  wide?: boolean
  mobileOverlay?: boolean
}>(), {
  asideWidthClass: 'w-72',
  contentOffsetClass: 'md:ml-72',
  navOffsetClass: 'md:left-72',
})

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// The builder-style frame: full-width top bar with corner-pinned controls and
// the sidebar tucked below it. App shells always get it; other sections request
// it explicitly via fullWidthNav.
const stackedNav = computed(() => props.appShell || props.fullWidthNav)

// Sidebar state. Initialised synchronously (before first paint) so a
// mobile-default-collapsed section never flashes its panel open then shut.
const isSidebarCollapsed = ref(getInitialCollapsed())

function getInitialCollapsed(): boolean {
  if (typeof window === 'undefined') return false
  if (props.storageKey) {
    const saved = localStorage.getItem(props.storageKey)
    if (saved !== null) return saved === 'true'
  }
  if (props.mobileDefaultCollapsed && window.innerWidth < 768) return true
  return false
}

// Check if a navigation item is active
const isActivePath = (item: NavigationItem): boolean => {
  if (item.exact) {
    return route.path === item.to
  }
  return route.path.startsWith(item.to)
}

// Toggle sidebar collapsed state
const toggleSidebar = () => {
  setSidebarCollapsed(!isSidebarCollapsed.value)
}

// Set the sidebar collapsed state directly (used by the mobile view switcher)
const setSidebarCollapsed = (collapsed: boolean) => {
  isSidebarCollapsed.value = collapsed
  if (props.storageKey) {
    localStorage.setItem(props.storageKey, isSidebarCollapsed.value ? 'true' : 'false')
  }
}

onMounted(() => {
  // Only check authentication if the current route requires it
  if (!authStore.isAuthenticated && route.meta.requiresAuth) {
    router.push({
      name: 'login',
      query: { redirect: route.fullPath }
    })
  }
})
</script>

<style scoped>
/* Note: never redefine Tailwind utilities (.w-72, .ml-72, ...) in here. Scoped
   rules compile with a [data-v-*] attribute selector, so they out-rank
   responsive variants like md:ml-72 and silently break them. Sizing is passed
   in as utility classes precisely to keep it out of here. */

/* One coordinated glide for the whole shell: the panel slides on transform,
   the content margin and navbar offset animate in lockstep on the same curve
   (matching the home page's reveal easing), so nothing tears or lags. */
.sidebar-panel {
  transition: transform 0.32s cubic-bezier(0.22, 1, 0.36, 1);
  will-change: transform;
}

.content-shell,
.navbar-shell {
  transition: margin 0.32s cubic-bezier(0.22, 1, 0.36, 1),
    left 0.32s cubic-bezier(0.22, 1, 0.36, 1);
}

@media (prefers-reduced-motion: reduce) {
  .sidebar-panel,
  .content-shell,
  .navbar-shell {
    transition: none;
  }
}

/* Active nav item: a quiet raised "crisp-card" pill rather than a heavy solid
   fill — reads as selected without shouting, matching the home page's card
   language. */
.nav-item-active {
  background: #ffffff;
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.05),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 3px 8px -3px rgba(15, 23, 42, 0.12);
}

:global(.dark) .nav-item-active {
  background: rgba(255, 255, 255, 0.07);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.08),
    0 1px 2px rgba(0, 0, 0, 0.4);
}

/* No tap flash on the toggle; keyboard focus shows the canonical ring via
   the focus-visible utilities on the button itself. */
:deep(.sidebar-toggle) {
  -webkit-tap-highlight-color: transparent;
}
</style>
