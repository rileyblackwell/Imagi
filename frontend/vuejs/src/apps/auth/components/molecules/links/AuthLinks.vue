<template>
  <div class="space-y-4">
    <!-- Enhanced Links Section -->
    <div class="text-center">
      <!-- Alternate Auth Action -->
      <p class="text-sm" style="color: var(--ink-55)">
        <template v-if="isLoginPage">
          New to Imagi?
          <router-link
            to="/auth/register"
            class="ml-1 pb-px font-medium text-ed-ink border-b border-b-ed-rule-strong [transition:border-color_0.18s_ease] hover:border-b-ed-accent
                   focus-visible:![outline:2px_solid_var(--accent)] focus-visible:![outline-offset:3px]"
          >
            Create an account
          </router-link>
        </template>
        <template v-else>
          Already have an account?
          <router-link
            to="/auth/signin"
            class="ml-1 pb-px font-medium text-ed-ink border-b border-b-ed-rule-strong [transition:border-color_0.18s_ease] hover:border-b-ed-accent
                   focus-visible:![outline:2px_solid_var(--accent)] focus-visible:![outline-offset:3px]"
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
