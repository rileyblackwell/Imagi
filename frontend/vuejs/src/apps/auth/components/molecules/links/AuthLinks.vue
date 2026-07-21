<template>
  <div class="space-y-4">
    <!-- Enhanced Links Section -->
    <div class="text-center">
      <!-- Alternate Auth Action -->
      <p class="text-blue-950/65 dark:text-blue-100/65 text-sm transition-colors duration-300">
        <template v-if="isLoginPage">
          New to Imagi?
          <router-link
            to="/auth/register"
            class="font-medium text-blue-950 dark:text-blue-100 border-b border-blue-950/25 dark:border-blue-100/30 hover:border-blue-950/60 dark:hover:border-blue-100/70 pb-0.5 transition-colors duration-200 ml-1 rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
          >
            Create an account
          </router-link>
        </template>
        <template v-else>
          Already have an account?
          <router-link
            to="/auth/signin"
            class="font-medium text-blue-950 dark:text-blue-100 border-b border-blue-950/25 dark:border-blue-100/30 hover:border-blue-950/60 dark:hover:border-blue-100/70 pb-0.5 transition-colors duration-200 ml-1 rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
          >
            Sign in here
          </router-link>
        </template>
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isLoginPage = computed(() => route.path === '/auth/signin')
</script>
