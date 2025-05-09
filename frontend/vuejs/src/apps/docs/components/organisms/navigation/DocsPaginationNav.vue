<template>
  <div class="mt-10 flex justify-between items-center">
    <router-link 
      v-if="prevLink"
      :to="prevLink.to" 
      class="inline-flex items-center px-4 py-2 bg-primary-500/20 hover:bg-primary-500/30 text-primary-400 rounded-lg transition-all duration-300"
    >
      <i class="fas fa-arrow-left mr-2"></i>
      {{ prevLink.text }}
    </router-link>
    <div v-else></div>
    
    <router-link 
      v-if="nextLink"
      :to="nextLink.to" 
      class="inline-flex items-center px-5 py-2.5 bg-gradient-to-r from-primary-500 to-violet-500 text-white rounded-lg hover:from-primary-600 hover:to-violet-600 shadow-lg shadow-primary-500/20 hover:shadow-primary-500/30 transform hover:-translate-y-1 transition-all duration-300"
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