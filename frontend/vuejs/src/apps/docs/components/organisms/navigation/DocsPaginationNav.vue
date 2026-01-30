<template>
  <div class="mt-10 flex justify-between items-center">
    <router-link 
      v-if="prevLink"
      :to="prevLink.to" 
      class="inline-flex items-center px-6 py-3 bg-white dark:bg-white border border-gray-200 dark:border-gray-300 text-gray-900 dark:text-black rounded-full font-medium hover:shadow-md transition-all duration-300"
    >
      <i class="fas fa-arrow-left mr-2"></i>
      {{ prevLink.text }}
    </router-link>
    <div v-else></div>
    
    <router-link 
      v-if="nextLink"
      :to="nextLink.to" 
      class="inline-flex items-center px-6 py-3 bg-gradient-to-b from-gray-800 via-gray-900 to-gray-950 dark:from-white dark:via-gray-50 dark:to-gray-100 text-white dark:text-gray-900 rounded-full font-medium border border-gray-700/50 dark:border-gray-300/50 hover:shadow-lg transition-all duration-300"
    >
      {{ nextLink.text }}
      <i class="fas fa-arrow-right ml-2"></i>
    </router-link>
    <div v-else></div>
  </div>
</template>

<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router';

interface LinkData {
  text: string;
  to: RouteLocationRaw;
}

defineProps<{
  prevLink?: LinkData;
  nextLink?: LinkData;
}>();
</script> 