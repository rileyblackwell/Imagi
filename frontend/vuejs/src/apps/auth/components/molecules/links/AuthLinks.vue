<template>
  <div class="mt-6 sm:mt-8 space-y-4 sm:space-y-6">
    <!-- Enhanced divider with animation -->
    <div class="relative">
      <div class="absolute inset-0 flex items-center">
        <div class="w-full h-px bg-gradient-to-r from-transparent via-dark-700/70 to-transparent"></div>
      </div>
      <div class="relative flex justify-center text-sm">
        <span class="px-4 bg-dark-800/70 backdrop-blur-sm text-gray-400 rounded-full">or</span>
      </div>
    </div>

    <!-- Enhanced Links Section -->
    <div class="text-center space-y-5 sm:space-y-6">
      <!-- Alternate Auth Action with enhanced styling -->
      <div class="transform hover:scale-[1.01] transition-all duration-300">
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

      <!-- Home Link with glow effect removed -->
      <router-link 
        to="/" 
        class="inline-flex items-center gap-2 px-4 sm:px-5 py-2.5 sm:py-3 rounded-xl text-gray-300 
               hover:text-white transition-all duration-300 group hover:bg-dark-700/70
               text-sm sm:text-base backdrop-blur-sm border border-transparent
               hover:border-primary-400/20 transform hover:-translate-y-1"
      >
        <i class="fas fa-arrow-left text-xs sm:text-sm transform group-hover:-translate-x-1.5 transition-transform duration-500"></i>
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

<style scoped>
/* Subtle pulse animation for the divider */
@keyframes pulse-slow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

.h-px {
  animation: pulse-slow 4s ease-in-out infinite;
}
</style>