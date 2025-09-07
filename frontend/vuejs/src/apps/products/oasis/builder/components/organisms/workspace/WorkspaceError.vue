<template>
  <div class="flex-1 flex flex-col h-full overflow-hidden relative z-10">
    <div class="flex flex-col items-center justify-center h-full p-12 text-center">
      <!-- Modern Error Container -->
      <div class="relative group max-w-xl w-full transform transition-all duration-300 hover:-translate-y-1">
        <!-- Enhanced glassmorphism Error Card -->
        <div class="absolute -inset-0.5 rounded-2xl opacity-70 bg-gradient-to-r from-red-500/50 to-rose-500/50 blur-md"></div>
        <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/95 via-dark-900/90 to-dark-800/95 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
          <!-- Sleek gradient header -->
          <div class="h-1 w-full bg-gradient-to-r from-red-400 via-rose-400 to-red-400 opacity-80"></div>

          <!-- Subtle background effects -->
          <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-red-400/4 to-rose-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>

          <div class="relative z-10 p-8">
            <!-- Modern pill badge -->
            <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-red-500/15 to-rose-500/15 border border-red-400/20 rounded-full mb-6 backdrop-blur-sm mx-auto">
              <div class="w-1.5 h-1.5 bg-red-400 rounded-full mr-2 animate-pulse"></div>
              <span class="text-red-300 font-medium text-xs tracking-wide uppercase">Workspace Error</span>
            </div>

            <!-- Error Icon -->
            <div class="w-16 h-16 bg-gradient-to-br from-red-500/20 to-rose-500/20 border border-red-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <i class="fas fa-exclamation-triangle text-2xl text-red-400"></i>
            </div>

            <!-- Error Content -->
            <h2 class="text-2xl font-semibold text-white mb-4">Something went wrong</h2>
            <p class="text-gray-300 mb-8 leading-relaxed">{{ error }}</p>

            <!-- Action Buttons -->
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
              <router-link
                to="/products/oasis/builder/dashboard"
                class="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-400 hover:to-violet-400 text-white font-medium rounded-xl shadow-lg shadow-indigo-500/25 transition-all duration-200 transform hover:-translate-y-1"
              >
                <i class="fas fa-arrow-left mr-2"></i>
                Go to Dashboard
              </router-link>
              <button
                @click="$emit('retry')"
                class="inline-flex items-center justify-center px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-red-400/30 text-gray-300 hover:text-white font-medium rounded-xl transition-all duration-200"
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
