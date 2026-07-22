<template>
  <div
    v-if="showWarning"
    class="fixed inset-0 bg-blue-950/40 dark:bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 transition-colors duration-300"
  >
    <div class="session-warning-card bg-white/95 dark:bg-[#131418] border border-blue-950/[0.08] dark:border-white/[0.14] backdrop-blur-sm p-6 rounded-2xl max-w-md w-full mx-4 transition-colors duration-300">
      <div class="text-center">
        <svg
          class="w-12 h-12 text-orange-500 dark:text-orange-400 mx-auto mb-4 transition-colors duration-300"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>

        <h2 class="text-xl font-semibold tracking-tight text-blue-950 dark:text-white mb-2 transition-colors duration-300">
          Session Timeout Warning
        </h2>

        <p class="text-blue-950/65 dark:text-blue-100/65 mb-4 transition-colors duration-300">
          Your session will expire in {{ timeLeft }} minutes. Would you like to stay signed in?
        </p>

        <div class="flex justify-center space-x-4">
          <button
            @click="extendSession"
            class="inline-flex items-center justify-center px-5 py-2.5 rounded-full font-medium bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-colors duration-200 shadow-[0_1px_2px_rgba(23,37,84,0.2),0_3px_8px_-2px_rgba(23,37,84,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#131418]"
          >
            Stay Signed In
          </button>

          <button
            @click="logout"
            class="inline-flex items-center justify-center px-5 py-2.5 rounded-full font-medium border border-blue-950/[0.14] text-blue-950/80 hover:text-blue-950 hover:border-blue-950/30 hover:bg-blue-950/[0.03] dark:border-white/[0.16] dark:text-blue-100/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06] transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#131418]"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/shared/stores/auth'

const authStore = useAuthStore()
const showWarning = ref(false)
const timeLeft = ref(5)
let warningTimer: number | null = null
let countdownTimer: number | null = null

const WARNING_THRESHOLD = 5 * 60 * 1000 // 5 minutes before timeout
const COUNTDOWN_INTERVAL = 60 * 1000 // 1 minute

const startWarningTimer = () => {
  const sessionTimeout = authStore.sessionTimeout
  if (sessionTimeout) {
    const timeUntilWarning = sessionTimeout - WARNING_THRESHOLD
    warningTimer = window.setTimeout(() => {
      showWarning.value = true
      startCountdown()
    }, timeUntilWarning)
  }
}

const startCountdown = () => {
  timeLeft.value = 5
  countdownTimer = window.setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) {
      logout()
    }
  }, COUNTDOWN_INTERVAL)
}

const extendSession = async () => {
  try {
    await authStore.refreshToken()
    showWarning.value = false
    resetTimers()
    startWarningTimer()
  } catch (error) {
    // Failed to extend session - logout user
    logout()
  }
}

const logout = () => {
  authStore.logout()
  resetTimers()
}

const resetTimers = () => {
  if (warningTimer) {
    clearTimeout(warningTimer)
    warningTimer = null
  }
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
}

onMounted(() => {
  startWarningTimer()
})

onUnmounted(() => {
  resetTimers()
})
</script>

<style scoped>
/* Crisp card shadow recipe (matches marketing pages) */
.session-warning-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

:root.dark .session-warning-card,
.dark .session-warning-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}
</style>
