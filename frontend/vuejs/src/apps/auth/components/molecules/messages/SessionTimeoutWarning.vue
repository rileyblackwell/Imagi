<template>
  <div
    v-if="showWarning"
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
  >
    <div class="bg-dark-800 p-6 rounded-lg max-w-md w-full mx-4">
      <div class="text-center">
        <svg
          class="w-12 h-12 text-yellow-500 mx-auto mb-4"
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
        
        <h2 class="text-xl font-semibold text-white mb-2">
          Session Timeout Warning
        </h2>
        
        <p class="text-gray-400 mb-4">
          Your session will expire in {{ timeLeft }} minutes. Would you like to stay signed in?
        </p>

        <div class="flex justify-center space-x-4">
          <button
            @click="extendSession"
            class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors"
          >
            Stay Signed In
          </button>
          
          <button
            @click="logout"
            class="px-4 py-2 bg-dark-700 hover:bg-dark-600 text-gray-300 rounded-lg transition-colors"
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