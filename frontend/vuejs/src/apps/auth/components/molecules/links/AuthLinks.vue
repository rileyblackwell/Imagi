<template>
  <div class="space-y-4">
    <!-- Enhanced Links Section with premium styling -->
    <div class="text-center">
      <!-- Alternate Auth Action -->
      <p class="text-white/50 text-sm">
        <template v-if="isLoginPage">
          New to Imagi?
          <router-link 
            to="/auth/register" 
            class="text-violet-400 hover:text-violet-300 font-medium transition-colors duration-300 ml-1"
          >
            Create an account
          </router-link>
        </template>
        <template v-else>
          Already have an account?
          <router-link 
            to="/auth/login" 
            class="text-violet-400 hover:text-violet-300 font-medium transition-colors duration-300 ml-1"
          >
            Sign in here
          </router-link>
        </template>
      </p>
    </div>

    <!-- Home Link with premium styling -->
    <div class="text-center">
      <router-link 
        to="/" 
        class="group inline-flex items-center gap-2 px-5 py-2.5 rounded-xl 
               text-white/50 hover:text-white/90
               bg-white/[0.03] hover:bg-white/[0.06]
               border border-white/[0.08] hover:border-white/[0.15]
               transition-all duration-300 text-sm font-medium"
      >
        <i class="fas fa-arrow-left text-xs transform group-hover:-translate-x-1 transition-transform duration-300"></i>
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
