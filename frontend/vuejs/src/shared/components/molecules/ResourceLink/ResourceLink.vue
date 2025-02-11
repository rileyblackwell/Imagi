<template>
  <a
    :href="url"
    class="block p-4 rounded-lg transition-colors hover:bg-dark-800 border border-dark-700"
  >
    <div class="flex items-start gap-4">
      <div class="flex-shrink-0">
        <i :class="[icon, 'text-primary-500 text-lg']"></i>
      </div>
      <div class="flex-1 min-w-0">
        <h4 class="text-sm font-medium text-white mb-1">{{ title }}</h4>
        <p class="text-sm text-gray-400">{{ description }}</p>
      </div>
      <div class="flex-shrink-0">
        <i class="fas fa-chevron-right text-gray-500"></i>
      </div>
    </div>
  </a>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description: string
  icon: string
  url: string
}>()
</script>
