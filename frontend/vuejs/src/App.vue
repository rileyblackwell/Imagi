<template>
  <div id="app" class="min-h-screen bg-dark-950 text-white flex flex-col">
    <router-view v-slot="{ Component }" class="flex-grow">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    <NotificationToast />
  </div>
</template>

<script setup lang="ts">
import { NotificationToast } from '@/shared/components/atoms';
import { useAuthStore } from '@/apps/auth/store'
import { onMounted } from 'vue'

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
</script>

