<template>
  <div class="flex-1 flex flex-col h-full overflow-hidden relative z-10">
    <div class="flex flex-col items-center justify-center h-full p-12 text-center">
      <!-- Clean Error Container -->
      <div class="relative max-w-xl w-full transition-all duration-300">
        <!-- Clean Error Card -->
        <div class="crisp-card relative rounded-2xl border border-blue-200/70 dark:border-blue-300/[0.16] bg-white dark:bg-white/[0.05] overflow-hidden transition-all duration-300">
          <div class="relative p-8">
            <!-- Error Icon -->
            <div class="w-16 h-16 bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800/30 rounded-2xl flex items-center justify-center mx-auto mb-6 transition-colors duration-300">
              <i class="fas fa-exclamation-triangle text-2xl text-red-600 dark:text-red-400"></i>
            </div>

            <!-- Error Content -->
            <h2 class="text-2xl font-semibold text-blue-950 dark:text-white mb-4 transition-colors duration-300">Something went wrong</h2>
            <p class="text-blue-950/70 dark:text-blue-100/70 mb-8 leading-relaxed transition-colors duration-300">{{ error }}</p>

            <!-- Action Buttons -->
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
              <router-link
                to="/imagi/projects"
                class="group inline-flex items-center justify-center px-6 py-3 rounded-full font-medium bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-colors duration-200 shadow-[0_1px_2px_rgba(23,37,84,0.2),0_3px_8px_-2px_rgba(23,37,84,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
              >
                <i class="fas fa-arrow-left mr-2"></i>
                <span>Go to Dashboard</span>
              </router-link>
              <button
                @click="$emit('retry')"
                class="inline-flex items-center justify-center px-6 py-3 rounded-full border border-blue-950/[0.14] dark:border-white/[0.16] bg-white dark:bg-white/[0.03] hover:bg-blue-950/[0.03] dark:hover:bg-white/[0.06] hover:border-blue-950/30 dark:hover:border-white/30 text-blue-950/80 dark:text-blue-100/80 hover:text-blue-950 dark:hover:text-white shadow-sm hover:shadow-md transition-all duration-300 font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
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

<style scoped>
/* Crisp, sharply-defined card matching Home/About/Projects */
.crisp-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.dark .crisp-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}

</style>
