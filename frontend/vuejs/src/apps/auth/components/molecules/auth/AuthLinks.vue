<template>
  <div class="mt-6 sm:mt-8 space-y-4 sm:space-y-6">
    <!-- Divider -->
    <div class="relative">
      <div class="absolute inset-0 flex items-center">
        <div class="w-full border-t border-dark-700/50"></div>
      </div>
      <div class="relative flex justify-center text-sm">
        <span class="px-4 bg-dark-800/50 text-gray-400">or</span>
      </div>
    </div>

    <!-- Links Section -->
    <div class="text-center space-y-4 sm:space-y-6">
      <!-- Alternate Auth Action -->
      <div>
        <p class="text-gray-300 text-sm sm:text-base">
          <template v-if="isLoginPage">
            New to Imagi?
            <router-link 
              to="/auth/register" 
              class="text-primary-400 hover:text-primary-300 font-medium transition-colors duration-300"
            >
              Create an account
            </router-link>
          </template>
          <template v-else>
            Already have an account?
            <router-link 
              to="/auth/login" 
              class="text-primary-400 hover:text-primary-300 font-medium transition-colors duration-300"
            >
              Sign in here
            </router-link>
          </template>
        </p>
      </div>

      <!-- Home Link -->
      <router-link 
        to="/" 
        class="inline-flex items-center gap-2 px-3 sm:px-4 py-2 rounded-lg text-gray-400 
               hover:text-white transition-all duration-300 group hover:bg-dark-700/50
               text-sm sm:text-base"
      >
        <i class="fas fa-arrow-left text-xs sm:text-sm transform group-hover:-translate-x-1 transition-transform"></i>
        Back to Home
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isLoginPage = computed(() => route.path === '/auth/login')
</script>