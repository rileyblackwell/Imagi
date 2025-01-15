<template>
  <div id="app" class="min-h-screen bg-dark-950 text-white">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { onMounted } from 'vue'

export default {
  name: 'App',
  setup() {
    const authStore = useAuthStore()

    onMounted(async () => {
      try {
        // Initialize auth state on app mount
        await authStore.initAuth()
      } catch (error) {
        console.error('Failed to initialize auth:', error)
        // Continue loading the app even if auth fails
      }
    })
  }
}
</script>

<style>
/* Base styles */
:root {
  --color-dark-950: #0a0b0f;
  --color-dark-900: #111318;
  --color-dark-800: #1a1d24;
  --color-dark-700: #282c35;
  --color-primary-400: #60a5fa;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--color-dark-950);
  color: white;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Utility classes */
.bg-gradient-radial {
  background: radial-gradient(circle at top right, var(--tw-gradient-from), var(--tw-gradient-to));
}

.shadow-glow {
  box-shadow: 0 0 25px -5px var(--color-primary-500);
}
</style>
