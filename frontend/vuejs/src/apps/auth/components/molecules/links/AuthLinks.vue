<template>
  <div class="space-y-4">
    <!-- Enhanced Links Section -->
    <div class="text-center">
      <!-- Alternate Auth Action -->
      <p class="text-blue-950/70 dark:text-blue-100/70 text-sm transition-colors duration-300">
        <template v-if="isLoginPage">
          New to Imagi?
          <router-link
            to="/auth/register"
            class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 font-medium transition-colors duration-200 ml-1"
          >
            Create an account
          </router-link>
        </template>
        <template v-else>
          Already have an account?
          <router-link
            to="/auth/signin"
            class="text-blue-700 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-200 font-medium transition-colors duration-200 ml-1"
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
