<template>
  <div class="text-center">
    <div v-if="loading" class="space-y-4">
      <i class="fas fa-circle-notch fa-spin fa-2x text-primary-500"></i>
      <p class="text-gray-400">Verifying your email...</p>
    </div>

    <div v-else-if="verified" class="space-y-4">
      <i class="fas fa-check-circle fa-2x text-green-500"></i>
      <h3 class="text-xl text-white">Email Verified!</h3>
      <p class="text-gray-400">Your email has been verified. You can now log in.</p>
      <button
        @click="router.push('/auth/login')"
        class="mt-4 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
      >
        Go to Login
      </button>
    </div>

    <div v-else-if="error" class="space-y-4">
      <i class="fas fa-exclamation-circle fa-2x text-red-500"></i>
      <h3 class="text-xl text-white">Verification Failed</h3>
      <p class="text-red-400">{{ error }}</p>
      <button
        @click="router.push('/auth/login')"
        class="mt-4 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
      >
        Go to Login
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/apps/auth/store'
import { AuthHeader } from '@/apps/auth/components'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const verified = ref(false)
const error = ref(null)

onMounted(async () => {
  const key = route.params.key
  if (!key) {
    error.value = 'Invalid verification link'
    loading.value = false
    return
  }

  try {
    await authStore.verifyEmail(key)
    verified.value = true
  } catch (err) {
    error.value = err.message || 'Verification failed'
  } finally {
    loading.value = false
  }
})
</script>
