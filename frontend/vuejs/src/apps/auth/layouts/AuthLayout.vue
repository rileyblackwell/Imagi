<!-- Auth Layout - Clean minimal design matching Home page -->
<template>
  <DefaultLayout>
    <!-- Clean full-screen layout matching Home page design -->
    <div class="min-h-screen bg-white dark:bg-[#0a0a0a] relative overflow-hidden transition-colors duration-500">
      <!-- Minimal background with subtle texture - matching Home page -->
      <div class="fixed inset-0 pointer-events-none">
        <!-- Subtle gradient - very minimal -->
        <div class="absolute inset-0 bg-gradient-to-b from-gray-50/50 via-white to-white dark:from-[#0a0a0a] dark:via-[#0a0a0a] dark:to-[#0a0a0a] transition-colors duration-500"></div>
        
        <!-- Very subtle grid pattern for texture (dark mode only) -->
        <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]" 
             style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
      </div>

      <!-- Content wrapper with proper spacing -->
      <div class="flex min-h-screen w-full relative z-10">
        <div class="w-full flex items-center justify-center px-4 sm:px-6 py-16 pt-28 sm:pt-32">
          <!-- Clean Auth Container -->
          <div class="w-full max-w-[520px] mx-auto">
            <!-- Clean card with subtle shadow -->
            <div class="relative animate-fade-in">
              <div class="relative rounded-2xl border border-gray-200/80 dark:border-white/[0.08] bg-white dark:bg-[#0a0a0f]/50 shadow-sm dark:shadow-none backdrop-blur-xl overflow-hidden transition-all duration-300">
                <!-- Card content -->
                <div class="relative z-10 p-8 sm:p-10">
                  <!-- Logo and Title Section -->
                  <div class="text-center mb-10">
                    <div class="inline-flex items-center justify-center mb-8">
                      <ImagiLogo size="xl" to="/" />
                    </div>
                    
                    <!-- Title -->
                    <h2 class="text-xl sm:text-2xl font-medium tracking-tight mb-3 leading-[1.2] text-black dark:text-white transition-colors duration-300">
                      {{ route.meta.title }}
                    </h2>
                    <p class="text-base text-gray-500 dark:text-white/80 leading-relaxed transition-colors duration-300">
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
              </div>
            </div>
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

<style scoped>
/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Fade in animation */
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.8s ease-out forwards;
}
</style>
