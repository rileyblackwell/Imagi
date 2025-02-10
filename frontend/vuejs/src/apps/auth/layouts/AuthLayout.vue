<!-- Auth Layout -->
<template>
  <DefaultLayout>
    <!-- Changed structure to ensure footer appears at bottom -->
    <div class="w-full min-h-screen bg-dark-900">
      <!-- Content wrapper with proper spacing -->
      <div class="flex min-h-screen w-full">
        <div class="w-full flex items-center justify-center px-4 py-16 pt-28 sm:pt-32 relative">
          <!-- Background Elements -->
          <div class="fixed inset-0">
            <!-- Base gradient -->
            <div class="absolute inset-0 bg-gradient-to-br from-primary-400/30 via-dark-900 to-violet-400/30"></div>
          
            <!-- Ambient glow -->
            <div class="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[600px] 
                        bg-gradient-to-r from-blue-400/30 via-primary-400/30 to-violet-400/30 
                        rounded-full blur-[120px] opacity-90"></div>
            
            <!-- Corner accents -->
            <div class="absolute -top-40 -right-40 w-96 h-96 bg-indigo-400/30 rounded-full blur-[100px]"></div>
            <div class="absolute -bottom-40 -left-40 w-96 h-96 bg-blue-400/30 rounded-full blur-[100px]"></div>
            
            <!-- Additional highlights -->
            <div class="absolute top-1/3 left-0 w-72 h-72 bg-primary-300/20 rounded-full blur-[80px]"></div>
            <div class="absolute bottom-1/3 right-0 w-72 h-72 bg-violet-300/20 rounded-full blur-[80px]"></div>
            
            <!-- Grid pattern -->
            <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
          </div>

          <!-- Auth Container -->
          <div class="w-full max-w-[420px] mx-auto relative z-10">
            <div class="bg-dark-900/70 backdrop-blur-xl rounded-2xl p-6 sm:p-8 border border-dark-800/50 
                        hover:border-primary-300/40 transition-all duration-500 
                        shadow-[0_0_60px_-12px_rgba(59,130,246,0.35)]">
              <!-- Enhanced Logo and Title Section -->
              <div class="text-center mb-8">
                <div class="inline-block p-4 rounded-xl bg-gradient-to-br from-primary-500/20 via-violet-500/20 
                            to-indigo-500/20 border border-primary-400/30 mb-6 group 
                            hover:from-primary-500/30 hover:via-violet-500/30 hover:to-indigo-500/30 
                            transition-all duration-500 hover:border-primary-400/40
                            shadow-[0_0_30px_-12px_rgba(59,130,246,0.4)]
                            hover:shadow-[0_0_40px_-12px_rgba(59,130,246,0.5)]">
                  <h1 class="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-primary-300 via-violet-300 
                             to-indigo-300 bg-clip-text text-transparent tracking-tight
                             group-hover:from-primary-200 group-hover:via-violet-200 group-hover:to-indigo-200 
                             transition-all duration-500">
                    Imagi
                  </h1>
                </div>
                <h2 class="text-2xl sm:text-3xl font-bold text-white mb-3 tracking-tight">
                  {{ $route.meta.title }}
                </h2>
                <p class="text-base sm:text-lg text-gray-200/90">
                  {{ $route.meta.subtitle }}
                </p>
              </div>

              <!-- Main Content -->
              <div class="relative">
                <router-view />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { DefaultLayout } from '@/shared/layouts'
import { AuthLinks, AuthHeader } from '@/apps/auth/components'
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
</style>