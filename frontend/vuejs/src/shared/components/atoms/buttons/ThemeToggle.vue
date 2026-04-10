<template>
  <div 
    class="relative inline-flex items-center gap-1 p-1 rounded-full bg-gray-200/80 dark:bg-white/10 backdrop-blur-sm border border-gray-300/50 dark:border-white/20 transition-all duration-300"
    role="group"
    aria-label="Theme selector"
  >
    <!-- Sliding background indicator -->
    <div 
      class="absolute top-1 h-[calc(100%-0.5rem)] rounded-full bg-white dark:bg-white/20 shadow-sm transition-all duration-300 ease-out"
      :style="indicatorStyle"
    ></div>

    <!-- System option -->
    <button
      @click="selectTheme('system')"
      :class="[
        'relative z-10 flex items-center justify-center px-3 py-1.5 rounded-full transition-all duration-300',
        currentTheme === 'system' 
          ? 'text-gray-900 dark:text-white' 
          : 'text-gray-600 dark:text-white/60 hover:text-gray-800 dark:hover:text-white/80'
      ]"
      :title="'System theme' + (currentTheme === 'system' ? ` (${effectiveTheme})` : '')"
      aria-label="Use system theme"
    >
      <i class="fas fa-laptop text-sm"></i>
    </button>

    <!-- Light option -->
    <button
      @click="selectTheme('light')"
      :class="[
        'relative z-10 flex items-center justify-center px-3 py-1.5 rounded-full transition-all duration-300',
        currentTheme === 'light' 
          ? 'text-amber-600 dark:text-amber-400' 
          : 'text-gray-600 dark:text-white/60 hover:text-amber-500 dark:hover:text-amber-400'
      ]"
      title="Light theme"
      aria-label="Use light theme"
    >
      <i class="fas fa-sun text-sm" :class="{ 'animate-pulse-subtle': currentTheme === 'light' }"></i>
    </button>

    <!-- Dark option -->
    <button
      @click="selectTheme('dark')"
      :class="[
        'relative z-10 flex items-center justify-center px-3 py-1.5 rounded-full transition-all duration-300',
        currentTheme === 'dark' 
          ? 'text-indigo-600 dark:text-indigo-400' 
          : 'text-gray-600 dark:text-white/60 hover:text-indigo-500 dark:hover:text-indigo-400'
      ]"
      title="Dark theme"
      aria-label="Use dark theme"
    >
      <i class="fas fa-moon text-sm"></i>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useThemeStore } from '@/shared/stores/theme'

const themeStore = useThemeStore()

const currentTheme = computed(() => themeStore.currentTheme)
const effectiveTheme = computed(() => themeStore.effectiveTheme)

const indicatorStyle = computed(() => {
  const buttonWidth = 40 // approximate width in pixels
  const positions = {
    system: '0.25rem',
    light: `calc(0.25rem + ${buttonWidth}px)`,
    dark: `calc(0.25rem + ${buttonWidth * 2}px)`
  }
  
  return {
    left: positions[currentTheme.value],
    width: `${buttonWidth}px`
  }
})

const selectTheme = (theme: 'light' | 'dark' | 'system') => {
  themeStore.setTheme(theme)
}
</script>

<style scoped>
/* Subtle pulse animation for sun */
@keyframes pulse-subtle {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

.animate-pulse-subtle {
  animation: pulse-subtle 2s ease-in-out infinite;
}

/* Smooth hover effects */
button {
  position: relative;
}

button:active {
  transform: scale(0.95);
}
</style>
