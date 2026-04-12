<template>
  <!-- CTA Section - Clean Design matching homepage -->
  <div class="py-8 mt-8">
    <div class="relative">
      <!-- Card content -->
      <div class="relative p-8 md:p-10 rounded-2xl border border-gray-200 dark:border-white/[0.08] bg-gray-50 dark:bg-white/[0.02] backdrop-blur-xl overflow-hidden transition-colors duration-300">
        <!-- Content layout -->
        <div class="flex flex-col items-start gap-6">
          <!-- Text content -->
          <div class="flex-1">
            <h2 class="text-2xl md:text-3xl font-semibold text-gray-900 dark:text-white/90 mb-4 leading-tight transition-colors duration-300">
              {{ title }}
            </h2>
            
            <p class="text-base md:text-lg text-gray-600 dark:text-white/60 mb-8 leading-relaxed max-w-xl transition-colors duration-300">
              {{ description }}
            </p>
            
            <!-- Primary Button - black text with no hover effects -->
            <router-link 
              :to="buttonLink"
              class="inline-flex items-center justify-center gap-3 px-7 py-3.5 bg-transparent text-gray-900 dark:text-white rounded-full font-medium text-base border border-gray-300 dark:border-white/20"
            >
              <span>{{ buttonText }}</span>
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  title: string;
  icon: string;
  description: string;
  buttonText: string;
  buttonLink: string;
  buttonIcon: string;
}>(), {
  title: 'Ready to Get Started?',
  icon: 'fas fa-lightbulb',
  description: 'Follow our step-by-step guide to create your first project and see Imagi in action.',
  buttonText: 'Quick Start Guide',
  buttonLink: '/docs/quickstart',
  buttonIcon: 'fas fa-arrow-right'
});
</script>
