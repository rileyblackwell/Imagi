<template>
  <div class="flex-1 flex flex-col h-full overflow-hidden relative z-10">
    <div class="flex flex-col items-center justify-center h-full p-12 text-center">
      <!-- Clean Error Container -->
      <div class="relative max-w-xl w-full transition-all duration-300">
        <!-- Clean Error Card -->
        <div class="relative rounded-2xl border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] shadow-lg overflow-hidden transition-all duration-300">
          <div class="relative p-8">
            <!-- Error Icon -->
            <div class="w-16 h-16 bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800/30 rounded-2xl flex items-center justify-center mx-auto mb-6 transition-colors duration-300">
              <i class="fas fa-exclamation-triangle text-2xl text-red-600 dark:text-red-400"></i>
            </div>

            <!-- Error Content -->
            <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4 transition-colors duration-300">Something went wrong</h2>
            <p class="text-gray-600 dark:text-white/60 mb-8 leading-relaxed transition-colors duration-300">{{ error }}</p>

            <!-- Action Buttons -->
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
              <router-link
                to="/products/imagi/projects"
                class="inline-flex items-center justify-center px-6 py-3 rounded-xl border border-gray-200 dark:border-white/[0.08] bg-gradient-to-b from-gray-800 via-gray-900 to-gray-950 dark:from-white dark:via-gray-50 dark:to-gray-100 text-white dark:text-gray-900 shadow-lg hover:shadow-xl transition-all duration-300 font-semibold"
              >
                <i class="fas fa-arrow-left mr-2"></i>
                Go to Dashboard
              </router-link>
              <button
                @click="$emit('retry')"
                class="inline-flex items-center justify-center px-6 py-3 rounded-xl border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-white/[0.03] hover:bg-gray-50 dark:hover:bg-white/[0.06] text-gray-700 dark:text-white/70 hover:text-gray-900 dark:hover:text-white shadow-sm hover:shadow-md transition-all duration-300 font-medium"
              >
                <i class="fas fa-sync-alt mr-2"></i>
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ error: string | null | undefined }>()
</script>
