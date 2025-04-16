<!-- Auth Layout -->
<template>
  <DefaultLayout>
    <!-- Enhanced full-screen layout with improved background -->
    <div class="w-full min-h-screen bg-gradient-to-b from-dark-950 to-dark-900">
      <!-- Enhanced Background Elements -->
      <div class="fixed inset-0 overflow-hidden pointer-events-none">
        <!-- Base gradient -->
        <div class="absolute inset-0 bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950"></div>
        
        <!-- Enhanced gradient orbs with no animations -->
        <div class="absolute top-[10%] left-[5%] w-[300px] sm:w-[500px] md:w-[800px] h-[300px] sm:h-[500px] md:h-[800px] rounded-full bg-primary-500/5 blur-[80px] sm:blur-[120px]"></div>
        <div class="absolute bottom-[20%] right-[10%] w-[200px] sm:w-[400px] md:w-[600px] h-[200px] sm:h-[400px] md:h-[600px] rounded-full bg-violet-500/5 blur-[60px] sm:blur-[100px]"></div>
        
        <!-- Subtle corner accents -->
        <div class="absolute -top-40 -right-40 w-80 h-80 bg-primary-400/10 rounded-full blur-[100px]"></div>
        <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-violet-400/10 rounded-full blur-[100px]"></div>
        
        <!-- Subtle noise texture -->
        <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
      </div>

      <!-- Content wrapper with proper spacing -->
      <div class="flex min-h-screen w-full">
        <div class="w-full flex items-center justify-center px-4 py-16 pt-28 sm:pt-32 relative">
          <!-- Enhanced Auth Container -->
          <div class="w-full max-w-[480px] mx-auto relative z-10">
            <div class="bg-dark-900/70 backdrop-blur-xl rounded-2xl p-8 sm:p-10 
                        border border-dark-700/50
                        hover:border-primary-300/30 transition-all duration-500 
                        shadow-[0_10px_50px_-12px_rgba(0,0,0,0.5)]">
              <!-- Refined Logo and Title Section -->
              <div class="text-center mb-10">
                <div class="inline-flex items-center justify-center mb-8">
                  <ImagiLogo size="lg" to="/" class="transform hover:scale-105 transition-transform duration-300" />
                </div>
                <h2 class="text-2xl sm:text-3xl font-semibold text-white mb-3 tracking-tight">
                  {{ route.meta.title }}
                </h2>
                <p class="text-base text-gray-300/90 font-medium">
                  {{ route.meta.subtitle }}
                </p>
              </div>

              <!-- Main Content with transition -->
              <router-view v-slot="{ Component }">
                <transition name="fade" mode="out-in">
                  <component :is="Component" />
                </transition>
              </router-view>
            </div>
            
            <!-- Decorative elements -->
            <div class="absolute -z-10 -bottom-6 -right-6 w-16 sm:w-24 h-16 sm:h-24 bg-primary-500/10 rounded-full blur-xl"></div>
            <div class="absolute -z-10 -top-6 -left-6 w-24 sm:w-32 h-24 sm:h-32 bg-violet-500/10 rounded-full blur-xl"></div>
          </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup lang="ts">
import DefaultLayout from '@/shared/layouts/DefaultLayout.vue'
import { useRoute } from 'vue-router'
import { ImagiLogo } from '@/shared/components/molecules'

const route = useRoute()
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Noise texture */
.bg-noise {
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.15'/%3E%3C/svg%3E");
}
</style>