<template>
  <router-link 
    :to="to" 
    class="block p-4 bg-dark-900/50 border border-dark-800 hover:border-primary-500/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 group"
  >
    <div class="flex items-start space-x-4">
      <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
        <i :class="[icon, 'text-xl text-primary-400']"></i>
      </div>
      <div>
        <h3 class="text-white group-hover:text-primary-400 transition-colors font-medium text-lg">{{ title }}</h3>
        <p class="text-gray-400 text-sm">{{ description }}</p>
      </div>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router';

defineProps<{
  to: RouteLocationRaw;
  icon: string;
  title: string;
  description: string;
}>();
</script> 