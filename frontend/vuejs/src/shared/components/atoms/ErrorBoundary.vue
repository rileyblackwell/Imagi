<template>
  <div>
    <slot v-if="!error" />
    <div 
      v-else 
      class="flex flex-col items-center justify-center h-full p-8 bg-dark-900 text-white"
    >
      <h2 class="text-xl font-semibold mb-4">Something went wrong</h2>
      <p class="text-gray-400 mb-6">{{ error.message }}</p>
      <button
        class="px-4 py-2 bg-primary-500 hover:bg-primary-600 rounded-lg transition-colors"
        @click="handleReset"
      >
        Try Again
      </button>
      
      <!-- Debug Info (only shown in development) -->
      <details v-if="isDev" class="mt-8 text-sm text-gray-500">
        <summary class="cursor-pointer hover:text-gray-400">Debug Info</summary>
        <pre class="mt-2 p-4 bg-dark-800 rounded-lg overflow-auto">{{ error.stack }}</pre>
      </details>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'
import { useBuilderStore } from '@/apps/products/builder/stores/builderStore'

const error = ref<Error | null>(null)
const store = useBuilderStore()
const isDev = import.meta.env.DEV

const handleReset = () => {
  store.reset()
  error.value = null
  // Refresh the page as a last resort
  window.location.reload()
}

// Implement error capturing logic
onErrorCaptured((err: Error, vm, info) => {
  console.error('Error caught by boundary:', err, info)
  error.value = err
  // Prevent the error from propagating
  return false
})
</script> 