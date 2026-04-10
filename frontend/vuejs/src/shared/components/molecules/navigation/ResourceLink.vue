<template>
  <a
    :href="url"
    target="_blank"
    rel="noopener"
    class="block p-4 rounded-lg hover:bg-dark-700 transition-colors duration-200"
  >
    <div class="flex items-center">
      <i :class="[icon, 'text-primary-400 mr-3']"></i>
      <div class="flex-grow">
        <h4 class="text-white font-medium mb-1">{{ title }}</h4>
        <p class="text-gray-400 text-sm">{{ description }}</p>
      </div>
      <i class="fas fa-external-link-alt text-gray-500"></i>
    </div>
  </a>
</template>

<script setup lang="ts">
defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  url: {
    type: String,
    required: true
  }
})
</script>
