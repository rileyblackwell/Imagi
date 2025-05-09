<template>
  <DocsCard color-variant="primary">
    <DocsCardHeader :title="title" :icon="icon" />
    <p class="mb-4">
      {{ description }}
    </p>
    <router-link 
      :to="buttonLink" 
      class="relative group inline-flex items-center justify-center"
    >
      <!-- Blurred gradient background -->
      <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500 to-violet-500 rounded-xl blur opacity-75 group-hover:opacity-100 transition duration-300"></div>
      
      <!-- Button content -->
      <div class="relative flex items-center justify-center px-6 py-3 bg-dark-900 rounded-xl transition-all duration-300">
        <i :class="[buttonIcon, 'mr-2 text-primary-400 group-hover:text-primary-300']"></i>
        <span class="font-medium text-white">{{ buttonText }}</span>
        <i class="fas fa-arrow-right ml-2 text-primary-400 group-hover:text-primary-300 group-hover:translate-x-0.5 transition-transform duration-300"></i>
      </div>
    </router-link>
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
  buttonIcon: 'fas fa-rocket'
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