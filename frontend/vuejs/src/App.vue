<template>
  <div id="app" class="min-h-screen bg-light-50 dark:bg-dark-950 text-gray-900 dark:text-white flex flex-col transition-colors duration-300">
    <router-view v-slot="{ Component }" class="flex-grow">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup lang="ts">
import { useThemeStore } from '@/shared/stores/theme'

const themeStore = useThemeStore()

// Initialize synchronously (before mount) so the store takes over from the
// pre-paint inline script in index.html without a repaint in between.
themeStore.initializeTheme()
</script>
