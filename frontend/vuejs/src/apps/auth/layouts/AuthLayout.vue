<!-- Auth Layout -->
<template>
  <DefaultLayout>
    <!-- Changed structure to ensure footer appears at bottom -->
    <div class="w-full min-h-screen bg-dark-900">
      <!-- Content wrapper with proper spacing -->
      <div class="flex min-h-screen w-full">
        <div class="w-full flex items-center justify-center px-4 py-16 pt-28 sm:pt-32 relative">
          <!-- Enhanced Background Elements -->
          <div class="fixed inset-0">
            <!-- Base gradient -->
            <div class="absolute inset-0 bg-gradient-to-br from-primary-400/20 via-dark-900 to-violet-400/20"></div>
          
            <!-- Refined ambient glow -->
            <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] 
                        bg-gradient-to-r from-primary-400/20 via-violet-400/20 to-indigo-400/20 
                        rounded-full blur-[150px] opacity-80"></div>
            
            <!-- Subtle corner accents -->
            <div class="absolute -top-40 -right-40 w-80 h-80 bg-primary-400/20 rounded-full blur-[120px]"></div>
            <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-violet-400/20 rounded-full blur-[120px]"></div>
            
            <!-- Grid overlay -->
            <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.02]"></div>
          </div>

          <!-- Enhanced Auth Container -->
          <div class="w-full max-w-[440px] mx-auto relative z-10">
            <div class="bg-dark-900/80 backdrop-blur-2xl rounded-2xl p-8 sm:p-10 
                        border border-dark-700/50 shadow-xl
                        hover:border-primary-300/30 transition-all duration-500 
                        shadow-[0_8px_40px_-12px_rgba(0,0,0,0.5)]">
              <!-- Refined Logo and Title Section -->
              <div class="text-center mb-10">
                <div class="inline-flex items-center justify-center mb-8">
                  <div class="rounded-2xl bg-gradient-to-br p-[1px] from-primary-300/40 to-violet-300/40
                            hover:from-primary-200/50 hover:to-violet-200/50 transition-all duration-300">
                    <div class="px-6 py-3 rounded-2xl bg-dark-900/95 backdrop-blur-xl
                              shadow-[0_0_15px_-3px_rgba(99,102,241,0.4)]">
                      <h1 class="text-3xl font-bold bg-gradient-to-r from-pink-300 via-emerald-300 to-yellow-200 
                                bg-clip-text text-transparent tracking-tight
                                drop-shadow-[0_0_12px_rgba(236,72,153,0.3)]
                                animate-gradient">
                        Imagi
                      </h1>
                    </div>
                  </div>
                </div>
                <h2 class="text-2xl sm:text-3xl font-semibold text-white mb-3 tracking-tight">
                  {{ $route.meta.title }}
                </h2>
                <p class="text-base text-gray-300/90 font-medium">
                  {{ $route.meta.subtitle }}
                </p>
              </div>

              <!-- Main Content with transition -->
              <router-view v-slot="{ Component }">
                <transition name="fade" mode="out-in">
                  <component :is="Component" />
                </transition>
              </router-view>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { DefaultLayout } from '@/shared/layouts'
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.animate-gradient {
  background-size: 200% auto;
  animation: gradient-shift 4s ease infinite;
}
</style>