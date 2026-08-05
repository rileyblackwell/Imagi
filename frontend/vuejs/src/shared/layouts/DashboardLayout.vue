<!-- Global authenticated app shell: one sidebar engine for every workspace
     (docs, builder, …). The sidebar's surface, motion, collapse behaviour and
     the top-bar toggle are shared here; each section customises width and the
     panel's contents through props + slots.

     Collapsed means GONE: the panel slides fully off-canvas on every
     breakpoint and the content reclaims the full width. The only control that
     brings it back lives in the top bar (SidebarToggle), never inside the
     panel — so it can never disappear along with the thing it opens. -->
<template>
  <BaseLayout :app-shell="appShell">
    <!-- App-shell views (the builder workspace) fill the shell exactly and clip
         overflow, so nothing below can push the page taller than the viewport.
         BaseLayout takes the shell out of flow on top of this, which is what
         actually guarantees the document can never scroll — see the comment
         there for why sizing alone is not enough. -->
    <div class="flex" :class="appShell ? 'h-full min-h-0 overflow-hidden' : 'min-h-screen'">
      <!-- Sidebar: the same glass as the navbar (bg-white/80 blur + hairline),
           so the top bar and the panel read as one continuous frame around the
           page. On mobile it drops below the navbar and becomes an off-canvas
           drawer that floats over the content. -->
      <aside
        class="sidebar-panel fixed bottom-0 left-0 z-30 flex flex-col top-nav border-r border-blue-950/[0.08] dark:border-white/[0.08] bg-canvas/80 backdrop-blur-xl max-md:shadow-[0_24px_60px_-20px_rgba(15,23,42,0.35)] dark:max-md:shadow-[0_24px_60px_-20px_rgba(0,0,0,0.7)]"
        :class="[
          asideWidthClass,
          isSidebarCollapsed ? '-translate-x-full pointer-events-none' : 'translate-x-0'
        ]"
        :aria-hidden="isSidebarCollapsed ? 'true' : undefined"
      >
        <!-- Section header, when the section supplies one. App shells like the
             builder put their own header inside #sidebar-content instead. -->
        <div
          v-if="$slots['sidebar-header']"
          class="flex-shrink-0 h-14 flex items-center gap-2 px-3 border-b border-blue-950/[0.08] dark:border-white/[0.08]"
        >
          <div class="flex-1 min-w-0">
            <slot name="sidebar-header"></slot>
          </div>
        </div>

        <!-- Custom Sidebar Content -->
        <div class="flex-1 min-h-0 overflow-hidden">
          <slot
            name="sidebar-content"
            :isSidebarCollapsed="isSidebarCollapsed"
            :toggleSidebar="toggleSidebar"
            :setSidebarCollapsed="setSidebarCollapsed"
          ></slot>
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
        <!-- Navbar. It anchors itself to the top of the viewport; this only
             restates the surface it wears inside the app shell. -->
        <BaseNavbar
          class="navbar-shell z-20 bg-canvas/80 backdrop-blur-md border-b border-blue-950/[0.08] dark:border-white/[0.08]"
          fluid
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
        </BaseNavbar>

        <!-- Main content area -->
        <main
          class="flex-1 flex flex-col relative pt-nav bg-canvas overflow-hidden"
          :class="appShell ? 'min-h-0' : ''"
        >
          <!-- setSidebarCollapsed reaches the content because the panel can be
               collapsed away entirely: whatever fills this slot may then be the
               only thing on screen, and needs its own way to bring it back. -->
          <slot
            :isSidebarCollapsed="isSidebarCollapsed"
            :setSidebarCollapsed="setSidebarCollapsed"
          ></slot>
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
          class="md:hidden fixed top-nav left-0 right-0 bottom-0 z-20 bg-blue-950/25 dark:bg-black/45 backdrop-blur-[1px]"
          aria-hidden="true"
          @click="setSidebarCollapsed(true)"
        ></div>
      </transition>
    </div>
  </BaseLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import BaseLayout from './BaseLayout.vue'
import { BaseNavbar, BaseFooter } from '@/shared/components'
// Not a public atom: this layout is its only consumer and styles it with :deep().
import SidebarToggle from '@/shared/components/atoms/buttons/SidebarToggle.vue'

const props = withDefaults(defineProps<{
  storageKey?: string
  // When true, this is a full-screen app shell (e.g. the builder workspace):
  // the site footer is dropped so the content fills the viewport exactly.
  appShell?: boolean
  // Per-section sizing. Passed as ready-made utility classes so the responsive
  // (md:) variants compose cleanly and there are no scoped-style specificity
  // fights. The content offset applies only at md+ — on mobile the panel
  // overlays, so the content is never pushed.
  asideWidthClass?: string
  contentOffsetClass?: string
  // Start collapsed on small screens (no stored preference yet) so a section
  // whose panel is a menu (docs) opens to its content, not the menu.
  mobileDefaultCollapsed?: boolean
  // Sections with their own mobile view switcher (the builder) suppress the
  // top-bar toggle on mobile to avoid two competing controls.
  hideToggleOnMobile?: boolean
}>(), {
  asideWidthClass: 'w-72',
  contentOffsetClass: 'md:ml-72',
})

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
  transition: transform 0.32s var(--app-ease);
  will-change: transform;
}

.content-shell,
.navbar-shell {
  transition: margin 0.32s var(--app-ease),
    left 0.32s var(--app-ease);
}

@media (prefers-reduced-motion: reduce) {
  .sidebar-panel,
  .content-shell,
  .navbar-shell {
    transition: none;
  }
}

/* No tap flash on the toggle; keyboard focus shows the canonical ring via
   the focus-visible utilities on the button itself. */
:deep(.sidebar-toggle) {
  -webkit-tap-highlight-color: transparent;
}
</style>
