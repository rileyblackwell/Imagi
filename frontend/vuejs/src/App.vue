<template>
  <div id="app" class="min-h-screen bg-dark-950 text-white flex flex-col">
    <router-view v-slot="{ Component }" class="flex-grow">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script>
import { useAuthStore } from '@/apps/auth/store'
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

