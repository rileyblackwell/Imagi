<template>
  <router-link
    v-if="route"
    :to="route"
    class="flex items-center justify-between p-3 rounded-lg bg-dark-800 hover:bg-dark-700 border border-dark-700 hover:border-primary-500/50 transition-all group"
  >
    <div class="flex items-center space-x-3">
      <div class="w-8 h-8 rounded-md bg-dark-700 border border-dark-600 flex items-center justify-center">
        <i :class="[icon, 'group-hover:text-primary-400 transition-colors']"></i>
      </div>
      <span class="font-medium text-white group-hover:text-primary-400 transition-colors">
        {{ title }}
      </span>
    </div>
    <i class="fas fa-chevron-right text-gray-400 group-hover:text-primary-400 transition-colors"></i>
  </router-link>
  <button
    v-else
    @click="$emit('click')"
    class="w-full flex items-center justify-between p-3 rounded-lg bg-dark-800 hover:bg-dark-700 border border-dark-700 hover:border-primary-500/50 transition-all group"
  >
    <div class="flex items-center space-x-3">
      <div class="w-8 h-8 rounded-md bg-dark-700 border border-dark-600 flex items-center justify-center">
        <i :class="[icon, 'group-hover:text-primary-400 transition-colors']"></i>
      </div>
      <span class="font-medium text-white group-hover:text-primary-400 transition-colors">
        {{ title }}
      </span>
    </div>
    <i class="fas fa-chevron-right text-gray-400 group-hover:text-primary-400 transition-colors"></i>
  </button>
</template>

<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router';

defineProps<{
  title: string;
  icon: string;
  route?: RouteLocationRaw;
}>();

defineEmits<{
  (e: 'click'): void;
}>();
</script>
