<template>
  <DocsCard color-variant="primary">
    <DocsCardHeader :title="title" :icon="icon" />
    <p class="text-gray-300 mb-6 leading-relaxed">
      {{ description }}
    </p>
    
    <!-- Modern separator -->
    <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-6"></div>
    
    <!-- Updated button to match QuickStart create project style -->
    <router-link 
      :to="buttonLink" 
      class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-indigo-500/20 to-violet-500/20 hover:from-indigo-500/30 hover:to-violet-500/30 text-indigo-300 hover:text-indigo-200 rounded-xl transition-all duration-300 border border-indigo-400/20 hover:border-indigo-400/30 group"
    >
      <i :class="buttonIcon" class="mr-2.5 text-base transition-colors duration-300"></i>
      {{ buttonText }}
      <svg class="w-4 h-4 ml-2.5 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>
      </svg>
    </router-link>
    
    <p class="text-xs text-gray-500 mt-4 text-center leading-relaxed">
      <svg class="w-3 h-3 inline mr-1.5 opacity-60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
      </svg>
      Start building in minutes, not months
    </p>
  </DocsCard>
</template>

<script setup lang="ts">
import { DocsCard, DocsCardHeader } from '../index';

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
  description: 'Follow our step-by-step guide to create your first project and see Imagi Oasis in action.',
  buttonText: 'Quick Start Guide',
  buttonLink: '/docs/quickstart',
  buttonIcon: 'fas fa-arrow-right'
});
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes pulse-horizontal {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(4px); }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

.animate-pulse-horizontal {
  animation: pulse-horizontal 1.5s ease-in-out infinite;
}
</style> 