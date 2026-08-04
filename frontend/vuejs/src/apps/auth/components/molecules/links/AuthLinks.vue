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
            class="auth-link"
          >
            Create an account
          </router-link>
        </template>
        <template v-else>
          Already have an account?
          <router-link
            to="/auth/signin"
            class="auth-link"
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

<style scoped>
.auth-link {
  margin-left: 0.25rem;
  font-weight: 500;
  color: var(--ink);
  border-bottom: 1px solid var(--rule-strong);
  padding-bottom: 1px;
  transition: border-color 0.18s ease;
}

.auth-link:hover {
  border-bottom-color: var(--accent);
}

.auth-link:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 3px;
}
</style>
