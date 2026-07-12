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
                class="btn-3d btn-accent group relative inline-flex items-center justify-center px-6 py-3 rounded-full text-blue-950 border border-white/60 dark:border-white/30 font-semibold overflow-hidden"
              >
                <span class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent"></span>
                <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-blue-900/15 to-transparent"></span>
                <i class="fas fa-arrow-left mr-2 relative"></i>
                <span class="relative">Go to Dashboard</span>
              </router-link>
              <button
                @click="$emit('retry')"
                class="inline-flex items-center justify-center px-6 py-3 rounded-full border border-blue-200/70 dark:border-white/[0.12] bg-white dark:bg-white/[0.03] hover:bg-blue-50 dark:hover:bg-white/[0.06] text-blue-950/80 dark:text-white/70 hover:text-blue-950 dark:hover:text-white shadow-sm hover:shadow-md transition-all duration-300 font-medium"
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

/* Soft 3D button matching the site's primary "Start Building" button */
.btn-3d {
  transform: translateY(0) translateZ(0);
  transition: transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease;
  box-shadow:
    0 1px 2px rgba(30, 58, 138, 0.14),
    0 4px 10px -2px rgba(30, 58, 138, 0.16),
    0 10px 20px -6px rgba(30, 58, 138, 0.18),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.12);
}

.btn-3d:active {
  transition-duration: 0.1s;
}

.btn-accent {
  background: linear-gradient(155deg, #dbeeff 0%, #b7ddf7 55%, #9ecdf3 100%);
}

.dark .btn-3d {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 10px 20px -6px rgba(0, 0, 0, 0.5),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.18);
}
</style>
