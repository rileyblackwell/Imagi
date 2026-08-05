<template>
  <div class="relative min-h-screen bg-light-50 dark:bg-dark-950 text-gray-900 dark:text-white flex flex-col transition-colors duration-300">
    <!-- No mode="out-in" here: with vue-router 5 + Vue 3.5 the out-in resume
         callback never fires, so <router-view> latches on an empty placeholder
         and every in-app navigation renders a blank page until a full reload. -->
    <router-view v-slot="{ Component }" class="flex-grow">
      <transition name="fade">
        <component :is="Component" />
      </transition>
    </router-view>

    <!-- Global toast notifications (create/delete feedback, auth prompts, etc.) -->
    <NotificationToast />
  </div>
</template>

<script setup lang="ts">
import { useThemeStore } from '@/shared/stores/theme'
import { NotificationToast } from '@/shared/components/atoms'

const themeStore = useThemeStore()

// Initialize synchronously (before mount) so the store takes over from the
// pre-paint inline script in index.html without a repaint in between.
themeStore.initializeTheme()
</script>

<style scoped>
/* Crossfade between routed pages. Without mode="out-in" both pages are in the
   DOM together for the duration, so the outgoing one is taken out of flow —
   otherwise it stacks above the incoming page and the document height (and
   scrollbar) visibly jumps on every navigation. */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* fade-leave-from as well as fade-leave-active: Vue adds leave-from, forces a
   reflow, and only then adds leave-active, so a rule that lives on -active
   alone leaves one forced layout pass with both pages in flow — enough for
   anything below the outgoing page to resolve its position against it. */
.fade-leave-from,
.fade-leave-active {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}

@media (prefers-reduced-motion: reduce) {
  .fade-enter-active,
  .fade-leave-active {
    transition: none;
  }
}
</style>
