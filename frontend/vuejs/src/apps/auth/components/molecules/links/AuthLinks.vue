<template>
  <div class="space-y-4">
    <!-- Enhanced Links Section -->
    <div class="text-center">
      <!-- Alternate Auth Action -->
      <p class="text-white text-sm transition-colors duration-300">
        <template v-if="isLoginPage">
          New to Imagi?
          <router-link 
            to="/auth/register" 
            class="text-black dark:text-white font-medium ml-1"
          >
            Create an account
          </router-link>
        </template>
        <template v-else>
          Already have an account?
          <router-link 
            to="/auth/login" 
            class="text-black dark:text-white hover:text-gray-600 dark:hover:text-white/70 font-medium transition-colors duration-200 ml-1"
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
const isLoginPage = computed(() => route.path === '/auth/login')
</script>
